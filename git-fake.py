import os
import random
from datetime import datetime, timedelta
from faker import Faker
from git import Repo, Actor
import shutil

class GitCommitGenerator:
    def __init__(self, repo_path='fake_repo'):
        self.repo_path = os.path.abspath(repo_path)
        self.fake = Faker()
        self.repo = None
        self.authors = [
            Actor("Alice Developer", "alice@example.com"),
            Actor("Bob Contributor", "bob@example.com"),
            Actor("Charlie Maintainer", "charlie@example.com")
        ]
        self.existing_files = set()
        
    def initialize_repo(self):
        """初始化或清空Git仓库"""
        if os.path.exists(self.repo_path):
            shutil.rmtree(self.repo_path)
        os.makedirs(self.repo_path)
        self.repo = Repo.init(self.repo_path)
        self.existing_files = set()
        
    def _create_file(self, file_name):
        """创建新文件并返回完整路径"""
        file_path = os.path.join(self.repo_path, file_name)
        with open(file_path, 'w') as f:
            f.write(self.fake.text(max_nb_chars=random.randint(50, 500)))
        self.existing_files.add(file_name)
        return file_path
        
    def _modify_file(self, file_name):
        """修改现有文件并返回完整路径"""
        file_path = os.path.join(self.repo_path, file_name)
        with open(file_path, 'a') as f:
            f.write("\n" + self.fake.sentence())
        return file_path
        
    def _delete_file(self, file_name):
        """删除文件并返回文件名"""
        file_path = os.path.join(self.repo_path, file_name)
        os.remove(file_path)
        self.existing_files.remove(file_name)
        return file_path
        
    def generate_random_file_change(self):
        """生成随机文件变更，返回变更的文件名"""
        if not self.existing_files or random.random() < 0.3:  # 30%几率创建新文件
            file_name = f"file_{len(self.existing_files)+1}.txt"
            return self._create_file(file_name)
        else:
            file_name = random.choice(list(self.existing_files))
            action = random.choice(['modify', 'delete'])
            if action == 'modify':
                return self._modify_file(file_name)
            else:
                return self._delete_file(file_name)
    
    def generate_commit_date(self, start_date=None, days_back=365):
        """生成合理的提交时间序列"""
        if not start_date:
            start_date = datetime.now()
        random_days = random.randint(0, days_back)
        random_seconds = random.randint(0, 86400)
        return start_date - timedelta(days=random_days, seconds=random_seconds)
    
    def generate_commit(self, date=None):
        """生成单个提交"""
        try:
            file_path = self.generate_random_file_change()
            if not file_path:
                return False
                
            author = random.choice(self.authors)
            commit_message = self.fake.sentence()
            if random.random() > 0.7:
                commit_message += "\n\n" + self.fake.paragraph()
            
            # 使用GitPython的git命令直接操作
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
            
            return True
        except Exception as e:
            print(f"提交失败: {e}")
            return False
    
    def generate_history(self, num_commits=20, days_back=365):
        """生成提交历史"""
        self.initialize_repo()
        
        # 生成时间序列（确保时间递增）
        commit_dates = sorted(
            [self.generate_commit_date(days_back=days_back) for _ in range(num_commits)],
            reverse=True
        )
        
        for date in commit_dates:
            success = False
            attempts = 0
            while not success and attempts < 3:  # 最多尝试3次
                success = self.generate_commit(date)
                attempts += 1
        
        print(f"Generated {num_commits} commits in {self.repo_path}")

if __name__ == "__main__":
    generator = GitCommitGenerator()
    generator.generate_history(num_commits=50, days_back=180)

