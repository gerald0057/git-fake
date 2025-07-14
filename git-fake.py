import os
import random
import argparse
import logging
from datetime import datetime, timedelta
from faker import Faker
from git import Repo, Actor
import shutil

class GitCommitGenerator:
    def __init__(self, repo_path='fake_repo', log_level=logging.INFO):
        self.repo_path = os.path.abspath(repo_path)
        self.fake = Faker()
        self.repo = None
        self.authors = [
            Actor("Alice Developer", "alice@example.com"),
            Actor("Bob Contributor", "bob@example.com"),
            Actor("Charlie Maintainer", "charlie@example.com")
        ]
        self.existing_files = set()
        
        # Initialize logging
        self.logger = self._setup_logger(log_level)
        
    def _setup_logger(self, log_level):
        """Set up logger"""
        logger = logging.getLogger('GitCommitGenerator')
        logger.setLevel(log_level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = os.path.join(os.path.dirname(self.repo_path), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'git_generator.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error log file handler
        error_log_file = os.path.join(log_dir, 'git_generator_errors.log')
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        return logger

    def initialize_repo(self):
        """Initialize or load Git repository"""
        self.logger.info(f"Initializing repository: {self.repo_path}")
        
        try:
            if not os.path.exists(self.repo_path):
                self.logger.info(f"Creating new directory: {self.repo_path}")
                os.makedirs(self.repo_path)
                self.repo = Repo.init(self.repo_path)
                self.existing_files = set()
                self.logger.info(f"Git repository initialized: {self.repo_path}")
            else:
                if not os.path.exists(os.path.join(self.repo_path, '.git')):
                    error_msg = f"Path {self.repo_path} is not a Git repository"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)
                
                self.repo = Repo(self.repo_path)
                self.scan_existing_files()
                self.logger.info(f"Loaded existing Git repository: {self.repo_path}")
                
        except Exception as e:
            self.logger.error(f"Repository initialization failed: {e}")
            raise
    
    def scan_existing_files(self):
        """Scan existing files in the repository"""
        self.logger.debug("Scanning existing files...")
        self.existing_files = set()
        file_count = 0
        
        try:
            for root, _, files in os.walk(self.repo_path):
                if '.git' in root:
                    continue
                for file in files:
                    rel_path = os.path.relpath(os.path.join(root, file), self.repo_path)
                    self.existing_files.add(rel_path)
                    file_count += 1
            
            self.logger.info(f"Scan completed, found {file_count} existing files")
            self.logger.debug(f"Existing files list: {list(self.existing_files)}")
            
        except Exception as e:
            self.logger.error(f"File scanning failed: {e}")
            raise
        
    def _create_file(self, file_name):
        """Create new file and return full path"""
        self.logger.debug(f"Creating new file: {file_name}")
        
        try:
            file_path = os.path.join(self.repo_path, file_name)
            content = self.fake.text(max_nb_chars=random.randint(50, 500))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.existing_files.add(file_name)
            self.logger.info(f"File created successfully: {file_name}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"File creation failed {file_name}: {e}")
            raise
        
    def _modify_file(self, file_name):
        """Modify existing file and return full path"""
        self.logger.debug(f"Modifying file: {file_name}")
        
        try:
            file_path = os.path.join(self.repo_path, file_name)
            additional_content = "\n" + self.fake.sentence()
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(additional_content)
            
            self.logger.info(f"File modified successfully: {file_name}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"File modification failed {file_name}: {e}")
            raise
        
    def _delete_file(self, file_name):
        """Delete file and return file name"""
        self.logger.debug(f"Deleting file: {file_name}")
        
        try:
            file_path = os.path.join(self.repo_path, file_name)
            os.remove(file_path)
            self.existing_files.remove(file_name)
            self.logger.info(f"File deleted successfully: {file_name}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"File deletion failed {file_name}: {e}")
            raise
        
    def generate_random_file_change(self):
        """Generate random file change, return changed file name"""
        try:
            if not self.existing_files or random.random() < 0.3:  # 30% chance to create new file
                file_name = f"file_{len(self.existing_files)+1}.txt"
                self.logger.debug(f"Selected operation: create new file {file_name}")
                return self._create_file(file_name)
            else:
                file_name = random.choice(list(self.existing_files))
                action = random.choice(['modify', 'delete'])
                self.logger.debug(f"Selected operation: {action} file {file_name}")
                
                if action == 'modify':
                    return self._modify_file(file_name)
                else:
                    return self._delete_file(file_name)
                    
        except Exception as e:
            self.logger.error(f"File change operation failed: {e}")
            return None
    
    def generate_commit_date(self, start_date=None, days_back=365):
        """Generate reasonable commit time series"""
        if not start_date:
            start_date = datetime.now()
        random_days = random.randint(0, days_back)
        random_seconds = random.randint(0, 86400)
        commit_date = start_date - timedelta(days=random_days, seconds=random_seconds)
        
        self.logger.debug(f"Generated commit time: {commit_date}")
        return commit_date
    
    def generate_commit(self, date=None):
        """Generate single commit"""
        try:
            self.logger.debug(f"Starting commit generation, time: {date}")
            
            file_path = self.generate_random_file_change()
            if not file_path:
                self.logger.warning("File change failed, skipping this commit")
                return False
                
            author = random.choice(self.authors)
            commit_message = self.fake.sentence()
            if random.random() > 0.7:
                commit_message += "\n\n" + self.fake.paragraph()
            
            self.logger.debug(f"Commit message: {commit_message[:50]}...")
            self.logger.debug(f"Commit author: {author.name} <{author.email}>")
            
            # Use GitPython's git command directly
            self.repo.git.add('--all')
            
            if date:
                date_str = date.strftime('%Y-%m-%d %H:%M:%S')
                self.repo.git.commit(
                    '-m', commit_message,
                    '--date', date_str,
                    '--author', f"{author.name} <{author.email}>"
                )
            else:
                self.repo.git.commit(
                    '-m', commit_message,
                    '--author', f"{author.name} <{author.email}>"
                )
            
            self.logger.info(f"Commit successful - Author: {author.name}, Time: {date or 'current'}")
            return True
            
        except Exception as e:
            self.logger.error(f"Commit failed: {e}")
            return False
    
    def get_repo_statistics(self):
        """Get repository statistics"""
        try:
            if not self.repo:
                return None
                
            stats = {}
            
            # Basic information
            stats['repo_path'] = self.repo_path
            stats['is_bare'] = self.repo.bare
            stats['active_branch'] = self.repo.active_branch.name if not self.repo.bare else 'N/A'
            
            # Commit information
            commits = list(self.repo.iter_commits())
            stats['total_commits'] = len(commits)
            
            if commits:
                stats['first_commit'] = commits[-1].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
                stats['last_commit'] = commits[0].committed_datetime.strftime('%Y-%m-%d %H:%M:%S')
            else:
                stats['first_commit'] = 'N/A'
                stats['last_commit'] = 'N/A'
            
            # Author statistics
            authors = {}
            for commit in commits:
                author = commit.author.name
                if author in authors:
                    authors[author] += 1
                else:
                    authors[author] = 1
            
            stats['authors'] = authors
            stats['total_authors'] = len(authors)
            
            # File statistics
            stats['total_files'] = len(self.existing_files)
            stats['files_list'] = list(self.existing_files)
            
            # Branch information
            branches = [ref.name for ref in self.repo.refs if ref.name.startswith('refs/heads/')]
            stats['branches'] = branches
            stats['total_branches'] = len(branches)
            
            # Repository size (approximate)
            repo_size = 0
            for root, dirs, files in os.walk(self.repo_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.exists(file_path):
                        repo_size += os.path.getsize(file_path)
            
            stats['repo_size_mb'] = round(repo_size / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get repository statistics: {e}")
            return None
    
    def display_repo_info(self):
        """Display repository detailed information"""
        self.logger.info("=" * 60)
        self.logger.info("Git Repository Detailed Information")
        self.logger.info("=" * 60)
        
        stats = self.get_repo_statistics()
        if not stats:
            self.logger.error("Unable to get repository statistics")
            return
        
        # Basic information
        self.logger.info(f"Repository Path: {stats['repo_path']}")
        self.logger.info(f"Is Bare Repository: {'Yes' if stats['is_bare'] else 'No'}")
        self.logger.info(f"Current Branch: {stats['active_branch']}")
        self.logger.info(f"Repository Size: {stats['repo_size_mb']} MB")
        
        # Commit information
        self.logger.info("-" * 40)
        self.logger.info("Commit Information:")
        self.logger.info(f"  Total Commits: {stats['total_commits']}")
        self.logger.info(f"  First Commit: {stats['first_commit']}")
        self.logger.info(f"  Last Commit: {stats['last_commit']}")
        
        # Author information
        self.logger.info("-" * 40)
        self.logger.info("Author Information:")
        self.logger.info(f"  Total Authors: {stats['total_authors']}")
        for author, count in sorted(stats['authors'].items(), key=lambda x: x[1], reverse=True):
            self.logger.info(f"  {author}: {count} commits")
        
        # Branch information
        self.logger.info("-" * 40)
        self.logger.info("Branch Information:")
        self.logger.info(f"  Total Branches: {stats['total_branches']}")
        for branch in stats['branches']:
            self.logger.info(f"  {branch}")
        
        # File information
        self.logger.info("-" * 40)
        self.logger.info("File Information:")
        self.logger.info(f"  Total Files: {stats['total_files']}")
        if stats['files_list']:
            self.logger.info("  File List:")
            for file in sorted(stats['files_list']):
                self.logger.info(f"    {file}")
        
        self.logger.info("=" * 60)
    
    def get_recent_commits(self, limit=5):
        """Get recent commit information"""
        try:
            if not self.repo:
                return []
                
            commits = list(self.repo.iter_commits(max_count=limit))
            recent_commits = []
            
            for commit in commits:
                commit_info = {
                    'hash': commit.hexsha[:8],
                    'author': commit.author.name,
                    'date': commit.committed_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'message': commit.message.strip().split('\n')[0][:50]
                }
                recent_commits.append(commit_info)
                
            return recent_commits
            
        except Exception as e:
            self.logger.error(f"Failed to get recent commits: {e}")
            return []
    
    def display_recent_commits(self, limit=5):
        """Display recent commit information"""
        recent_commits = self.get_recent_commits(limit)
        if not recent_commits:
            self.logger.warning("No commits found")
            return
        
        self.logger.info(f"Recent {len(recent_commits)} commits:")
        self.logger.info("-" * 80)
        
        for commit in recent_commits:
            self.logger.info(f"[{commit['hash']}] {commit['date']} - {commit['author']}")
            self.logger.info(f"  {commit['message']}")
            self.logger.info("")
    
    def generate_history(self, num_commits=20, days_back=365):
        """Generate commit history"""
        self.logger.info(f"Starting commit history generation - Commits: {num_commits}, Time span: {days_back} days")
        
        try:
            # Record start time
            start_time = datetime.now()
            
            self.initialize_repo()
            
            # Display initial state
            initial_stats = self.get_repo_statistics()
            if initial_stats:
                self.logger.info(f"Repository state before generation: {initial_stats['total_commits']} commits, {initial_stats['total_files']} files")
            
            # Generate time series (ensure time increment)
            self.logger.debug("Generating commit time series...")
            commit_dates = sorted(
                [self.generate_commit_date(days_back=days_back) for _ in range(num_commits)],
                reverse=True
            )
            
            self.logger.debug(f"Time series generation completed, range: {commit_dates[-1]} to {commit_dates[0]}")
            
            successful_commits = 0
            failed_commits = 0
            
            for i, date in enumerate(commit_dates, 1):
                self.logger.info(f"Processing commit {i}/{num_commits}...")
                
                success = False
                attempts = 0
                max_attempts = 3
                
                while not success and attempts < max_attempts:
                    attempts += 1
                    self.logger.debug(f"Attempt {attempts}...")
                    success = self.generate_commit(date)
                    
                    if not success and attempts < max_attempts:
                        self.logger.warning(f"Attempt {attempts} failed, retrying...")
                
                if success:
                    successful_commits += 1
                else:
                    failed_commits += 1
                    self.logger.error(f"Commit {i} failed after {max_attempts} attempts")
            
            # Calculate execution time
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            self.logger.info(f"Commit history generation completed!")
            self.logger.info(f"Successful commits: {successful_commits}, Failed commits: {failed_commits}")
            self.logger.info(f"Execution time: {execution_time:.2f} seconds")
            
            # Display repository detailed information
            self.display_repo_info()
            
            # Display recent commits
            self.display_recent_commits(limit=min(10, successful_commits))
            
        except Exception as e:
            self.logger.error(f"Commit history generation failed: {e}")
            raise

def setup_argument_parser():
    """Set up command line argument parser"""
    parser = argparse.ArgumentParser(description='Generate fake Git commit history')
    parser.add_argument('--repo', type=str, default='fake_repo',
                       help='Repository path (default: fake_repo)')
    parser.add_argument('--num-commits', type=int, default=5,
                       help='Number of commits to generate (default: 5)')
    parser.add_argument('--days-back', type=int, default=10,
                       help='Time span in days (default: 10)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='Log level (default: INFO)')
    parser.add_argument('--show-info-only', action='store_true',
                       help='Only show existing repository information, do not generate new commits')
    return parser

if __name__ == "__main__":
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Convert log level
    log_level = getattr(logging, args.log_level.upper())
    
    try:
        generator = GitCommitGenerator(repo_path=args.repo, log_level=log_level)
        
        if args.show_info_only:
            # Info-only mode
            generator.initialize_repo()
            generator.display_repo_info()
            generator.display_recent_commits()
        else:
            # Normal generation mode
            generator.generate_history(num_commits=args.num_commits, days_back=args.days_back)
            
    except Exception as e:
        logging.error(f"Program execution failed: {e}")
        exit(1)
