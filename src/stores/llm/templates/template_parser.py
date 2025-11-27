import os
class TemplateParser:
    
    def __init__(self,language: str=None, default_language: str="en"):
        self.current_path = os.path.dirname(os.path.abspath(__file__))
        self.default_language = default_language

        self.set_language(language=language)
    
    def set_language(self, language: str):
        if not language:
            self.language = self.default_language
            return None
        language_path = os.path.join(self.current_path, 'locales', language)
        if language and os.path.exists(language_path):
            self.language = language
        else:
            self.language = self.default_language

    def get(self, group: str, key:str, vars:dict={}):
        if not group or not key:
            return None
        group_path = os.path.join(self.current_path, 'locales', self.language, f"{group}.py")
        if not os.path.exists(group_path):
            group_path = os.path.join(self.current_path, 'locales', self.default_language, f"{group}.py")
            if not os.path.exists(group_path):
                return None
        
        # import the group module
        module = __import__(f"stores.llm.templates.locales.{self.language}.{group}", fromlist=[group])
        if not module:
            module = __import__(f"stores.llm.templates.locales.{self.default_language}.{group}", fromlist=[group])
            if not module:
                return None
        key_attrribute = getattr(module, key, None)
        return key_attrribute.substitute(vars)



