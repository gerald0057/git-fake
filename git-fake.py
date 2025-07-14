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
        
        # 初始化日志记录
        self.logger = self._setup_logger(log_level)
        
    def _setup_logger(self, log_level):
        """设置日志记录器"""
        logger = logging.getLogger('GitCommitGenerator')
        logger.setLevel(log_level)
        
        # 清除现有的处理器
        logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        log_dir = os.path.join(os.path.dirname(self.repo_path), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_file = os.path.join(log_dir, 'git_generator.log')
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # 错误日志文件处理器
        error_log_file = os.path.join(log_dir, 'git_generator_errors.log')
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        return logger

    def initialize_repo(self):
        """初始化或加载Git仓库"""
        self.logger.info(f"初始化仓库: {self.repo_path}")
        
        try:
            if not os.path.exists(self.repo_path):
                self.logger.info(f"创建新目录: {self.repo_path}")
                os.makedirs(self.repo_path)
                self.repo = Repo.init(self.repo_path)
                self.existing_files = set()
                self.logger.info(f"Git仓库已初始化: {self.repo_path}")
            else:
                if not os.path.exists(os.path.join(self.repo_path, '.git')):
                    error_msg = f"路径 {self.repo_path} 不是一个Git仓库"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)
                
                self.repo = Repo(self.repo_path)
                self.scan_existing_files()
                self.logger.info(f"已加载现有Git仓库: {self.repo_path}")
                
        except Exception as e:
            self.logger.error(f"仓库初始化失败: {e}")
            raise
    
    def scan_existing_files(self):
        """扫描仓库中现有的文件"""
        self.logger.debug("扫描现有文件...")
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
            
            self.logger.info(f"扫描完成，发现 {file_count} 个现有文件")
            self.logger.debug(f"现有文件列表: {list(self.existing_files)}")
            
        except Exception as e:
            self.logger.error(f"文件扫描失败: {e}")
            raise
        
    def _create_file(self, file_name):
        """创建新文件并返回完整路径"""
        self.logger.debug(f"创建新文件: {file_name}")
        
        try:
            file_path = os.path.join(self.repo_path, file_name)
            content = self.fake.text(max_nb_chars=random.randint(50, 500))
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.existing_files.add(file_name)
            self.logger.info(f"文件创建成功: {file_name}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"文件创建失败 {file_name}: {e}")
            raise
        
    def _modify_file(self, file_name):
        """修改现有文件并返回完整路径"""
        self.logger.debug(f"修改文件: {file_name}")
        
        try:
            file_path = os.path.join(self.repo_path, file_name)
            additional_content = "\n" + self.fake.sentence()
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(additional_content)
            
            self.logger.info(f"文件修改成功: {file_name}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"文件修改失败 {file_name}: {e}")
            raise
        
    def _delete_file(self, file_name):
        """删除文件并返回文件名"""
        self.logger.debug(f"删除文件: {file_name}")
        
        try:
            file_path = os.path.join(self.repo_path, file_name)
            os.remove(file_path)
            self.existing_files.remove(file_name)
            self.logger.info(f"文件删除成功: {file_name}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"文件删除失败 {file_name}: {e}")
            raise
        
    def generate_random_file_change(self):
        """生成随机文件变更，返回变更的文件名"""
        try:
            if not self.existing_files or random.random() < 0.6:  # 30%几率创建新文件
                file_name = f"file_{len(self.existing_files)+1}.txt"
                self.logger.debug(f"选择操作: 创建新文件 {file_name}")
                return self._create_file(file_name)
            else:
                file_name = random.choice(list(self.existing_files))
                action = random.choice(['modify', 'delete'])
                self.logger.debug(f"选择操作: {action} 文件 {file_name}")
                
                if action == 'modify':
                    return self._modify_file(file_name)
                else:
                    return self._delete_file(file_name)
                    
        except Exception as e:
            self.logger.error(f"文件变更操作失败: {e}")
            return None
    
    def generate_commit_date(self, start_date=None, days_back=365):
        """生成合理的提交时间序列"""
        if not start_date:
            start_date = datetime.now()
        random_days = random.randint(0, days_back)
        random_seconds = random.randint(0, 86400)
        commit_date = start_date - timedelta(days=random_days, seconds=random_seconds)
        
        self.logger.debug(f"生成提交时间: {commit_date}")
        return commit_date
    
    def generate_commit(self, date=None):
        """生成单个提交"""
        try:
            self.logger.debug(f"开始生成提交，时间: {date}")
            
            file_path = self.generate_random_file_change()
            if not file_path:
                self.logger.warning("文件变更失败，跳过此次提交")
                return False
                
            author = random.choice(self.authors)
            commit_message = self.fake.sentence()
            if random.random() > 0.7:
                commit_message += "\n\n" + self.fake.paragraph()
            
            self.logger.debug(f"提交信息: {commit_message[:50]}...")
            self.logger.debug(f"提交作者: {author.name} <{author.email}>")
            
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
            
            self.logger.info(f"提交成功 - 作者: {author.name}, 时间: {date or 'current'}")
            return True
            
        except Exception as e:
            self.logger.error(f"提交失败: {e}")
            return False
    
    def generate_history(self, num_commits=20, days_back=365):
        """生成提交历史"""
        self.logger.info(f"开始生成提交历史 - 提交数量: {num_commits}, 时间跨度: {days_back}天")
        
        try:
            self.initialize_repo()
            
            # 生成时间序列（确保时间递增）
            self.logger.debug("生成提交时间序列...")
            commit_dates = sorted(
                [self.generate_commit_date(days_back=days_back) for _ in range(num_commits)],
                reverse=True
            )
            
            self.logger.debug(f"时间序列生成完成，范围: {commit_dates[-1]} 到 {commit_dates[0]}")
            
            successful_commits = 0
            failed_commits = 0
            
            for i, date in enumerate(commit_dates, 1):
                self.logger.info(f"正在处理第 {i}/{num_commits} 个提交...")
                
                success = False
                attempts = 0
                max_attempts = 3
                
                while not success and attempts < max_attempts:
                    attempts += 1
                    self.logger.debug(f"尝试第 {attempts} 次提交...")
                    success = self.generate_commit(date)
                    
                    if not success and attempts < max_attempts:
                        self.logger.warning(f"第 {attempts} 次尝试失败，重试...")
                
                if success:
                    successful_commits += 1
                else:
                    failed_commits += 1
                    self.logger.error(f"提交 {i} 在 {max_attempts} 次尝试后仍然失败")
            
            self.logger.info(f"提交历史生成完成！")
            self.logger.info(f"成功提交: {successful_commits}, 失败提交: {failed_commits}")
            self.logger.info(f"仓库路径: {self.repo_path}")
            
            # 显示最终统计
            total_files = len(self.existing_files)
            self.logger.info(f"最终文件数量: {total_files}")
            
        except Exception as e:
            self.logger.error(f"提交历史生成失败: {e}")
            raise

def setup_argument_parser():
    """设置命令行参数解析器"""
    parser = argparse.ArgumentParser(description='生成虚假的Git提交历史')
    parser.add_argument('--repo', type=str, default='fake_repo',
                       help='仓库路径 (默认: fake_repo)')
    parser.add_argument('--num-commits', type=int, default=5,
                       help='要生成的提交数量 (默认: 5)')
    parser.add_argument('--days-back', type=int, default=10,
                       help='时间跨度(天) (默认: 10)')
    parser.add_argument('--log-level', type=str, default='INFO',
                       choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       help='日志级别 (默认: INFO)')
    return parser

if __name__ == "__main__":
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # 转换日志级别
    log_level = getattr(logging, args.log_level.upper())
    
    try:
        generator = GitCommitGenerator(repo_path=args.repo, log_level=log_level)
        generator.generate_history(num_commits=args.num_commits, days_back=args.days_back)
    except Exception as e:
        logging.error(f"程序执行失败: {e}")
        exit(1)
