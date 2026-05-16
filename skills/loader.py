"""
技能系统 - 兼容 Hermes 技能格式
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from athena.logger import logger
from athena.config import settings
from athena.constants import BUILTIN_SKILLS_DIR, CUSTOM_SKILLS_DIR


@dataclass
class Skill:
    """技能定义"""
    
    name: str
    description: str
    category: Optional[str] = None
    version: str = "1.0.0"
    author: Optional[str] = None
    content: str = ""
    path: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "author": self.author,
            "path": str(self.path) if self.path else None
        }
    
    @classmethod
    def from_file(cls, path: Path) -> Optional['Skill']:
        """从 SKILL.md 文件加载技能（兼容Hermes格式）"""
        if not path.exists():
            return None
        
        content = path.read_text(encoding="utf-8")
        
        # Hermes技能格式：YAML frontmatter + markdown
        if content.startswith("---"):
            # 找到第二个 ---
            end_idx = content.find("---", 3)
            if end_idx != -1:
                yaml_part = content[3:end_idx].strip()
                md_part = content[end_idx+3:].strip()
                
                try:
                    frontmatter = yaml.safe_load(yaml_part)
                except Exception as e:
                    logger.warning(f"Failed to parse YAML frontmatter for {path}: {e}")
                    frontmatter = {}
                
                return cls(
                    name=frontmatter.get("name", path.parent.name),
                    description=frontmatter.get("description", ""),
                    category=frontmatter.get("category"),
                    version=frontmatter.get("version", "1.0.0"),
                    author=frontmatter.get("author"),
                    content=md_part,
                    path=path
                )
        
        # 无frontmatter，文件名作为名称
        return cls(
            name=path.parent.name,
            description="",
            content=content,
            path=path
        )


class SkillLoader:
    """技能加载器"""
    
    def __init__(self):
        self.skills: Dict[str, Skill] = {}
        self._load_builtin_skills()
        self._load_custom_skills()
        logger.info(f"Skill loader initialized, loaded {len(self.skills)} skills")
    
    def _load_builtin_skills(self) -> None:
        """加载内置技能"""
        self._load_from_dir(BUILTIN_SKILLS_DIR, is_builtin=True)
    
    def _load_custom_skills(self) -> None:
        """加载用户自定义技能"""
        self._load_from_dir(CUSTOM_SKILLS_DIR, is_builtin=False)
    
    def _load_from_dir(self, directory: Path, is_builtin: bool) -> None:
        """从目录加载技能"""
        if not directory.exists():
            return
        
        # 每个子目录是一个技能，包含 SKILL.md
        for skill_dir in directory.iterdir():
            if not skill_dir.is_dir():
                continue
            
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            
            skill = Skill.from_file(skill_file)
            if skill:
                self.skills[skill.name] = skill
                logger.debug(f"Loaded {'builtin' if is_builtin else 'custom'} skill: {skill.name}")
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict[str, Any]]:
        """列出所有技能"""
        return [s.to_dict() for s in self.skills.values()]
    
    def search_skills(self, query: str) -> List[Skill]:
        """搜索技能"""
        query = query.lower()
        results = []
        for skill in self.skills.values():
            if query in skill.name.lower() or query in skill.description.lower():
                results.append(skill)
        return results
    
    def reload(self) -> None:
        """重新加载所有技能"""
        self.skills.clear()
        self._load_builtin_skills()
        self._load_custom_skills()
        logger.info(f"Reloaded {len(self.skills)} skills")
