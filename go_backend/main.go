package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// Configuration for the server
type Config struct {
	Port        int    `json:"port"`
	GithubToken string `json:"github_token,omitempty"`
}

// Response structure for API calls
type Response struct {
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Data    interface{} `json:"data,omitempty"`
	Error   string      `json:"error,omitempty"`
}

// GitLFSOperation represents a git LFS operation request
type GitLFSOperation struct {
	Operation   string `json:"operation"`
	RepoPath    string `json:"repo_path"`
	FilePath    string `json:"file_path,omitempty"`
	URL         string `json:"url,omitempty"`
	GithubRepo  string `json:"github_repo,omitempty"`
	GithubOwner string `json:"github_owner,omitempty"`
	Branch      string `json:"branch,omitempty"`
}

func main() {
	// Default configuration
	config := Config{
		Port:        8001, // Default port (different from Python backend)
		GithubToken: os.Getenv("GITHUB_TOKEN"),
	}

	// Log GitHub token status (not the token itself)
	if config.GithubToken != "" {
		log.Println("GitHub token found in environment")
	} else {
		log.Println("No GitHub token found, GitHub operations may be limited")
	}

	// Set up routes
	http.HandleFunc("/health", healthCheckHandler)
	http.HandleFunc("/api/git-lfs", gitLFSHandler)
	http.HandleFunc("/api/github", githubHandler)

	// Start the server
	addr := fmt.Sprintf(":%d", config.Port)
	log.Printf("Starting Git LFS backend server on %s", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}

// healthCheckHandler provides a simple health check endpoint
func healthCheckHandler(w http.ResponseWriter, r *http.Request) {
	response := Response{
		Success: true,
		Message: "Git LFS backend is running",
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// gitLFSHandler handles all git LFS operations
func gitLFSHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		sendErrorResponse(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var operation GitLFSOperation
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&operation); err != nil {
		sendErrorResponse(w, "Invalid request body: "+err.Error(), http.StatusBadRequest)
		return
	}

	switch operation.Operation {
	case "init":
		handleGitLFSInit(w, operation)
	case "track":
		handleGitLFSTrack(w, operation)
	case "push":
		handleGitLFSPush(w, operation)
	case "pull":
		handleGitLFSPull(w, operation)
	case "status":
		handleGitLFSStatus(w, operation)
	default:
		sendErrorResponse(w, "Unknown operation: "+operation.Operation, http.StatusBadRequest)
	}
}

// handleGitLFSInit initializes git LFS in a repository
func handleGitLFSInit(w http.ResponseWriter, op GitLFSOperation) {
	if op.RepoPath == "" {
		sendErrorResponse(w, "Repository path is required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Run git lfs install
	cmd := exec.Command("git", "lfs", "install")
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to initialize Git LFS: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	response := Response{
		Success: true,
		Message: "Git LFS initialized successfully",
		Data:    string(output),
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// handleGitLFSTrack tracks files with git LFS
func handleGitLFSTrack(w http.ResponseWriter, op GitLFSOperation) {
	if op.RepoPath == "" || op.FilePath == "" {
		sendErrorResponse(w, "Repository path and file path are required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Run git lfs track
	cmd := exec.Command("git", "lfs", "track", op.FilePath)
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to track file with Git LFS: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	// Add .gitattributes to git
	cmd = exec.Command("git", "add", ".gitattributes")
	cmd.Dir = op.RepoPath
	_, err = cmd.CombinedOutput()
	if err != nil {
		log.Printf("Warning: Failed to add .gitattributes to git: %s", err.Error())
	}

	response := Response{
		Success: true,
		Message: fmt.Sprintf("File pattern '%s' is now tracked with Git LFS", op.FilePath),
		Data:    string(output),
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// handleGitLFSPush pushes LFS objects to the remote repository
func handleGitLFSPush(w http.ResponseWriter, op GitLFSOperation) {
	if op.RepoPath == "" {
		sendErrorResponse(w, "Repository path is required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Run git push with LFS
	cmd := exec.Command("git", "push")
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to push Git LFS objects: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	response := Response{
		Success: true,
		Message: "Git LFS objects pushed successfully",
		Data:    string(output),
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// handleGitLFSPull pulls LFS objects from the remote repository
func handleGitLFSPull(w http.ResponseWriter, op GitLFSOperation) {
	if op.RepoPath == "" {
		sendErrorResponse(w, "Repository path is required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Run git pull with LFS
	cmd := exec.Command("git", "pull")
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to pull Git LFS objects: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	response := Response{
		Success: true,
		Message: "Git LFS objects pulled successfully",
		Data:    string(output),
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// handleGitLFSStatus checks the status of LFS files in the repository
func handleGitLFSStatus(w http.ResponseWriter, op GitLFSOperation) {
	if op.RepoPath == "" {
		sendErrorResponse(w, "Repository path is required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Run git lfs status
	cmd := exec.Command("git", "lfs", "status")
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to get Git LFS status: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	response := Response{
		Success: true,
		Message: "Git LFS status retrieved successfully",
		Data:    string(output),
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// Helper function to check if a directory is a git repository
func isGitRepo(path string) bool {
	gitDir := filepath.Join(path, ".git")
	_, err := os.Stat(gitDir)
	return err == nil
}

// Helper function to send JSON responses
func sendJSONResponse(w http.ResponseWriter, data interface{}, statusCode int) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(statusCode)
	json.NewEncoder(w).Encode(data)
}

// githubHandler handles GitHub repository operations
func githubHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		sendErrorResponse(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var operation GitLFSOperation
	decoder := json.NewDecoder(r.Body)
	if err := decoder.Decode(&operation); err != nil {
		sendErrorResponse(w, "Invalid request body: "+err.Error(), http.StatusBadRequest)
		return
	}

	// Get GitHub token from environment
	githubToken := os.Getenv("GITHUB_TOKEN")
	if githubToken == "" && (operation.Operation == "clone" || operation.Operation == "pull" || operation.Operation == "push") {
		sendErrorResponse(w, "GitHub token is required for this operation", http.StatusBadRequest)
		return
	}

	switch operation.Operation {
	case "clone":
		handleGitHubClone(w, operation, githubToken)
	case "pull":
		handleGitHubPull(w, operation, githubToken)
	case "push":
		handleGitHubPush(w, operation, githubToken)
	case "status":
		handleGitHubStatus(w, operation)
	default:
		sendErrorResponse(w, "Unknown GitHub operation: "+operation.Operation, http.StatusBadRequest)
	}
}

// handleGitHubClone clones a GitHub repository
func handleGitHubClone(w http.ResponseWriter, op GitLFSOperation, token string) {
	if op.GithubOwner == "" || op.GithubRepo == "" || op.RepoPath == "" {
		sendErrorResponse(w, "GitHub owner, repository name, and local path are required", http.StatusBadRequest)
		return
	}

	// Create the directory if it doesn't exist
	if err := os.MkdirAll(op.RepoPath, 0755); err != nil {
		sendErrorResponse(w, "Failed to create directory: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// Check if the directory is empty
	entries, err := os.ReadDir(op.RepoPath)
	if err != nil {
		sendErrorResponse(w, "Failed to read directory: "+err.Error(), http.StatusInternalServerError)
		return
	}
	if len(entries) > 0 {
		sendErrorResponse(w, "Directory is not empty", http.StatusBadRequest)
		return
	}

	// Construct the GitHub URL with token for authentication
	repoURL := fmt.Sprintf("https://%s@github.com/%s/%s.git", token, op.GithubOwner, op.GithubRepo)
	if token == "" {
		// Use public URL if no token is provided
		repoURL = fmt.Sprintf("https://github.com/%s/%s.git", op.GithubOwner, op.GithubRepo)
	}

	// Clone the repository
	cmd := exec.Command("git", "clone", repoURL, ".")
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to clone repository: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	// Initialize Git LFS if it exists
	lfsCmd := exec.Command("git", "lfs", "install")
	lfsCmd.Dir = op.RepoPath
	lfsOutput, _ := lfsCmd.CombinedOutput()

	response := Response{
		Success: true,
		Message: fmt.Sprintf("Repository %s/%s cloned successfully", op.GithubOwner, op.GithubRepo),
		Data: map[string]string{
			"clone_output": string(output),
			"lfs_output":   string(lfsOutput),
		},
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// handleGitHubPull pulls changes from a GitHub repository
func handleGitHubPull(w http.ResponseWriter, op GitLFSOperation, token string) {
	if op.RepoPath == "" {
		sendErrorResponse(w, "Repository path is required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Set up GitHub credentials if token is provided
	if token != "" {
		credCmd := exec.Command("git", "config", "--local", "credential.helper", "store")
		credCmd.Dir = op.RepoPath
		credCmd.Run()

		// Store credentials temporarily
		credFile := filepath.Join(op.RepoPath, ".git", "credentials")
		os.WriteFile(credFile, []byte(fmt.Sprintf("https://%s:x-oauth-basic@github.com\n", token)), 0600)
		defer os.Remove(credFile)
	}

	// Pull the repository
	cmd := exec.Command("git", "pull")
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to pull repository: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	// Pull LFS objects if LFS is used
	lfsCmd := exec.Command("git", "lfs", "pull")
	lfsCmd.Dir = op.RepoPath
	lfsOutput, _ := lfsCmd.CombinedOutput()

	response := Response{
		Success: true,
		Message: "Repository pulled successfully",
		Data: map[string]string{
			"pull_output": string(output),
			"lfs_output":  string(lfsOutput),
		},
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// handleGitHubPush pushes changes to a GitHub repository
func handleGitHubPush(w http.ResponseWriter, op GitLFSOperation, token string) {
	if op.RepoPath == "" {
		sendErrorResponse(w, "Repository path is required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Set up GitHub credentials if token is provided
	if token != "" {
		credCmd := exec.Command("git", "config", "--local", "credential.helper", "store")
		credCmd.Dir = op.RepoPath
		credCmd.Run()

		// Store credentials temporarily
		credFile := filepath.Join(op.RepoPath, ".git", "credentials")
		os.WriteFile(credFile, []byte(fmt.Sprintf("https://%s:x-oauth-basic@github.com\n", token)), 0600)
		defer os.Remove(credFile)
	}

	// Push the repository
	cmd := exec.Command("git", "push")
	cmd.Dir = op.RepoPath
	output, err := cmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to push repository: %s\nOutput: %s", err.Error(), string(output)), http.StatusInternalServerError)
		return
	}

	response := Response{
		Success: true,
		Message: "Repository pushed successfully",
		Data:    string(output),
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// handleGitHubStatus checks the status of a GitHub repository
func handleGitHubStatus(w http.ResponseWriter, op GitLFSOperation) {
	if op.RepoPath == "" {
		sendErrorResponse(w, "Repository path is required", http.StatusBadRequest)
		return
	}

	// Check if the directory exists
	if _, err := os.Stat(op.RepoPath); os.IsNotExist(err) {
		sendErrorResponse(w, "Repository path does not exist", http.StatusBadRequest)
		return
	}

	// Check if it's a git repository
	if !isGitRepo(op.RepoPath) {
		sendErrorResponse(w, "Not a git repository", http.StatusBadRequest)
		return
	}

	// Get repository status
	statusCmd := exec.Command("git", "status")
	statusCmd.Dir = op.RepoPath
	statusOutput, err := statusCmd.CombinedOutput()
	if err != nil {
		sendErrorResponse(w, fmt.Sprintf("Failed to get repository status: %s\nOutput: %s", err.Error(), string(statusOutput)), http.StatusInternalServerError)
		return
	}

	// Get LFS status if available
	lfsCmd := exec.Command("git", "lfs", "status")
	lfsCmd.Dir = op.RepoPath
	lfsOutput, _ := lfsCmd.CombinedOutput()

	// Get remote URL
	remoteCmd := exec.Command("git", "remote", "get-url", "origin")
	remoteCmd.Dir = op.RepoPath
	remoteOutput, _ := remoteCmd.CombinedOutput()

	response := Response{
		Success: true,
		Message: "Repository status retrieved successfully",
		Data: map[string]string{
			"status":     string(statusOutput),
			"lfs_status": string(lfsOutput),
			"remote":     string(remoteOutput),
		},
	}
	sendJSONResponse(w, response, http.StatusOK)
}

// Helper function to send error responses
func sendErrorResponse(w http.ResponseWriter, errorMsg string, statusCode int) {
	response := Response{
		Success: false,
		Error:   errorMsg,
	}
	sendJSONResponse(w, response, statusCode)
}