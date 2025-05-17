#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <queue>
#include <unordered_set>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <chrono>
#include <algorithm>
#include <iomanip>
#include <limits> // Add this for numeric_limits

using namespace std;

// Structure to represent a page reference
struct PageReference {
    int pageId;
    string operation;
    string filename;
    bool isHit;
};

// Page Fault Analysis using FCFS Algorithm
class PageFaultAnalyzer {
private:
    vector<int> frames;
    queue<int> pageQueue;
    vector<PageReference> pageHistory;
    int frameSize;
    int pageFaults;
    int pageHits;
    
    // Log page fault information
    void logPageFault(int pageId, const string& operation, const string& filename, bool isHit) {
        PageReference ref;
        ref.pageId = pageId;
        ref.operation = operation;
        ref.filename = filename;
        ref.isHit = isHit;
        pageHistory.push_back(ref);
        
        // Also log to file
        ofstream logFile("page_fault_log.txt", ios::app);
        if (logFile) {
            auto now = chrono::system_clock::now();
            time_t currentTime = chrono::system_clock::to_time_t(now);
            logFile << ctime(&currentTime) << "Operation: " << operation 
                   << " | File: " << filename 
                   << " | Page ID: " << pageId
                   << " | " << (isHit ? "Hit" : "Page Fault") << endl;
            logFile.close();
        }
    }

public:
    PageFaultAnalyzer(int frames = 4) : frameSize(frames), pageFaults(0), pageHits(0) {}
    
    // Reset the analyzer
    void reset() {
        frames.clear();
        while (!pageQueue.empty()) {
            pageQueue.pop();
        }
        pageHistory.clear();
        pageFaults = 0;
        pageHits = 0;
    }
    
    // Process a page reference using FCFS
    bool processPageReference(int pageId, const string& operation, const string& filename) {
        // Check if page is already in frames (hit)
        auto it = find(frames.begin(), frames.end(), pageId);
        if (it != frames.end()) {
            pageHits++;
            logPageFault(pageId, operation, filename, true);
            return true;
        }
        
        // Page fault occurred
        pageFaults++;
        
        // If frames are full, remove the oldest page (FCFS)
        if (frames.size() >= frameSize && !frames.empty()) {
            int oldestPage = pageQueue.front();
            pageQueue.pop();
            frames.erase(remove(frames.begin(), frames.end(), oldestPage), frames.end());
        }
        
        // Add new page
        frames.push_back(pageId);
        pageQueue.push(pageId);
        logPageFault(pageId, operation, filename, false);
        return false;
    }
    
    // Display page fault analysis
    void displayAnalysis() {
        cout << "\n===== Page Fault Analysis =====" << endl;
        cout << "Total page references: " << (pageFaults + pageHits) << endl;
        cout << "Page hits: " << pageHits << endl;
        cout << "Page faults: " << pageFaults << endl;
        
        if (pageFaults + pageHits > 0) {
            double hitRatio = (double)pageHits / (pageFaults + pageHits) * 100;
            cout << "Hit ratio: " << fixed << setprecision(2) << hitRatio << "%" << endl;
        }
        
        cout << "\nCurrent pages in memory: ";
        for (int frame : frames) {
            cout << frame << " ";
        }
        cout << endl;
        
        // Display last 5 page references
        cout << "\nRecent page references:" << endl;
        cout << left << setw(10) << "Page ID" << setw(15) << "Operation" 
             << setw(20) << "Filename" << setw(10) << "Status" << endl;
        cout << string(55, '-') << endl;
        
        int start = max(0, (int)pageHistory.size() - 5);
        for (int i = start; i < pageHistory.size(); i++) {
            PageReference& ref = pageHistory[i];
            cout << left << setw(10) << ref.pageId << setw(15) << ref.operation 
                 << setw(20) << ref.filename << setw(10) 
                 << (ref.isHit ? "Hit" : "Fault") << endl;
        }
    }
    
    // Get statistics
    int getPageFaults() const { return pageFaults; }
    int getPageHits() const { return pageHits; }
};

class FileManagementSystem {
private:
    string loggedInUser;
    PageFaultAnalyzer pageAnalyzer;
    int nextPageId;
    
    // Generate a unique page ID based on operation and filename
    int generatePageId(const string& operation, const string& filename) {
        return nextPageId++;
    }
    
    // Log file operations
    void logOperation(const string& operation, const string& filename) {
        ofstream logFile("file_operations_log.txt", ios::app);
        if (logFile) {
            auto now = chrono::system_clock::now();
            time_t currentTime = chrono::system_clock::to_time_t(now);
            logFile << ctime(&currentTime) << "User: " << loggedInUser 
                   << " | Operation: " << operation 
                   << " | File: " << filename << endl;
            logFile.close();
        }
        
        // Process the operation for page fault analysis
        int pageId = generatePageId(operation, filename);
        pageAnalyzer.processPageReference(pageId, operation, filename);
    }

public:
    // Constructor
    FileManagementSystem() : loggedInUser(""), nextPageId(1) {}

    // Authentication Function (reads from users.txt)
    bool authenticate() {
        string username, password, fileUser, filePass;
        cout << "Enter username: ";
        cin >> username;
        cout << "Enter password: ";
        cin >> password;

        ifstream userFile("users.txt");
        if (!userFile) {
            cerr << "Error opening users file: " << strerror(errno) << endl;
            return false;
        }

        while (userFile >> fileUser >> filePass) {
            if (username == fileUser && password == filePass) {
                loggedInUser = username;
                userFile.close();
                cout << "Login successful! Welcome " << loggedInUser << endl;
                return true;
            }
        }

        userFile.close();
        cout << "Login failed! Invalid credentials." << endl;
        return false;
    }

    // Create File
    void createFile() {
        string filename;
        cout << "Enter file name: ";
        cin >> filename;

        string fullPath = loggedInUser + "_" + filename;

        int fd = open(fullPath.c_str(), O_WRONLY | O_CREAT, 0666);
        if (fd == -1) {
            cerr << "Error creating file: " << strerror(errno) << endl;
            return;
        }
        cout << "File '" << fullPath << "' created successfully." << endl;
        close(fd);
        
        logOperation("CREATE", fullPath);
    }

    // Write to File
    void writeToFile() {
        string filename;
        cout << "Enter file name: ";
        cin >> filename;

        string fullPath = loggedInUser + "_" + filename;

        ofstream file(fullPath, ios::app);
        if (!file) {
            cerr << "Error opening file: " << strerror(errno) << endl;
            return;
        }

        string content;
        cout << "Enter content: ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // Clear buffer properly
        getline(cin, content);

        file << content << endl;
        cout << "Content written successfully." << endl;

        file.close();
        
        logOperation("WRITE", fullPath);
    }

    // Modify File
    void modifyFile() {
        string filename;
        cout << "Enter file name to modify: ";
        cin >> filename;

        string fullPath = loggedInUser + "_" + filename;

        ofstream file(fullPath, ios::trunc);
        if (!file) {
            cerr << "Error opening file: " << strerror(errno) << endl;
            return;
        }

        string content;
        cout << "Enter new content: ";
        cin.ignore(numeric_limits<streamsize>::max(), '\n'); // Clear buffer properly
        getline(cin, content);

        file << content << endl;
        cout << "File modified successfully." << endl;

        file.close();
        
        logOperation("MODIFY", fullPath);
    }

    // Search Content in File
    void searchContent() {
        string filename, keyword;
        cout << "Enter file name: ";
        cin >> filename;
        cout << "Enter keyword to search: ";
        cin >> keyword;

        string fullPath = loggedInUser + "_" + filename;

        ifstream file(fullPath);
        if (!file) {
            cerr << "Error opening file: " << strerror(errno) << endl;
            return;
        }

        string line;
        bool found = false;
        while (getline(file, line)) {
            if (line.find(keyword) != string::npos) {
                cout << "Keyword found: " << line << endl;
                found = true;
            }
        }

        if (!found) cout << "Keyword not found in file." << endl;
        file.close();
        
        logOperation("SEARCH", fullPath);
    }

    // Read from File
    void readFromFile() {
        string filename;
        cout << "Enter file name: ";
        cin >> filename;

        string fullPath = loggedInUser + "_" + filename;

        ifstream file(fullPath);
        if (!file) {
            cerr << "Error opening file: " << strerror(errno) << endl;
            return;
        }

        string line;
        cout << "File Contents:" << endl;
        while (getline(file, line)) {
            cout << line << endl;
        }

        file.close();
        
        logOperation("READ", fullPath);
    }

    // Delete File
    void deleteFile() {
        string filename;
        cout << "Enter file name to delete: ";
        cin >> filename;

        string fullPath = loggedInUser + "_" + filename;

        if (remove(fullPath.c_str()) == 0) {
            cout << "File '" << fullPath << "' deleted successfully." << endl;
        } else {
            cerr << "Error deleting file: " << strerror(errno) << endl;
        }
        
        logOperation("DELETE", fullPath);
    }
    
    // View Page Fault Analysis
    void viewPageFaultAnalysis() {
        pageAnalyzer.displayAnalysis();
    }
    
    // Reset Page Fault Analysis
    void resetPageFaultAnalysis() {
        pageAnalyzer.reset();
        nextPageId = 1;
        cout << "Page fault analysis has been reset." << endl;
    }

    // Run the application
    void run() {
        if (!authenticate()) {
            return; // Exit if authentication fails
        }

        int choice;
        bool validInput;
        
        while (true) {
            cout << "\n==== Secure File Administration System ====" << endl;
            cout << "1. Create File" << endl;
            cout << "2. Write to File" << endl;
            cout << "3. Modify File" << endl;
            cout << "4. Search Content in File" << endl;
            cout << "5. Read from File" << endl;
            cout << "6. Delete File" << endl;
            cout << "7. View Page Fault Analysis" << endl;
            cout << "8. Reset Page Fault Analysis" << endl;
            cout << "9. Exit" << endl;
            cout << "Enter your choice: ";
            
            validInput = bool(cin >> choice);
            
            if (!validInput) {
                // Clear error flags
                cin.clear();
                // Discard invalid input
                cin.ignore(numeric_limits<streamsize>::max(), '\n');
                cout << "Invalid input! Please enter a number." << endl;
                continue;
            }

            switch (choice) {
                case 1: createFile(); break;
                case 2: writeToFile(); break;
                case 3: modifyFile(); break;
                case 4: searchContent(); break;
                case 5: readFromFile(); break;
                case 6: deleteFile(); break;
                case 7: viewPageFaultAnalysis(); break;
                case 8: resetPageFaultAnalysis(); break;
                case 9: cout << "Exiting..." << endl; return;
                default: cout << "Invalid choice! Try again." << endl;
            }
        }
    }
};

int main() {
    FileManagementSystem fms;
    fms.run();
    return 0;
}
