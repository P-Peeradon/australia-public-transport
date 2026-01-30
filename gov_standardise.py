import pandas as pd
import re

class OceaniaGovDataCleaner:
    def __init__(self):
        self.scope_name = {'Victoria': 'Melbourne', 'New South Wales': 'Sydney', 'Queensland': 'Brisbane', 'South Australia': 'Adelaide'}
        self.scope_code = {'NSW': 'SYD', 'VIC': 'MEL', 'SA': 'ADL' , 'QLD': 'BNE'}
        self.city_code_to_name = {'SYD': 'Sydney', 'ADL': 'Adelaide', 'MEL': 'Melbourne', 'BNE': 'Brisbane'}
    
    def clean_abs_csv(self, df: pd.DataFrame, city_code: str):
        '''
        Clean the csv data which is loaded and transformed from data loaded from ABS. Or, the data is directly downloaded from ABS.
        ABS = Australian Bureau Statistics.
        '''
        
        city_code = city_code.upper()
        if city_code not in self.scope_code:
            raise ValueError(f"'{city_code}' is not authorized for the Jan 2026 research phase.")
        if df is None or df.empty:
            raise ValueError("Data Exception: Provided DataFrame is empty.")
        
        df = df.copy()
        df['city_name'] = self.city_code_to_name[city_code]
        df['state_code'] = self.scope_code[city_code]
        
        df['sal_name_clean'] = df['sal_name'].apply(self.sanitize_legal_name)
        
        # Regex Capture: [Direction] [Base Name] or [Base Name] [Direction]

        temp_split = df['sal_name_clean'].apply(lambda x: pd.Series(self.split_name(x)))
        df['base_name'], df['direction'] = temp_split[0], temp_split[1]
        df['is_centre'] = (df['direction'] == "Centre").astype(int)
        
        return df
    
    def sanitize_legal_name(self, text):
        if not isinstance(text, str): return text
        # Removes: "City of", "Shire of", "Council", "LGA", etc.
        patterns = [r'^(The\s+)?(City|Shire|Town|Borough|District Council)\s+of\s+', 
                    r'\s+(City Council|Regional Council|LGA|Council)$']
        for p in patterns:
            text = re.sub(p, '', text, flags=re.IGNORECASE)
        return text.strip().title()
    
    @staticmethod
    def split_name(name):
        # Regex Capture: [Direction] [Base Name] or [Base Name] [Direction]
        pattern = r"^(North|South|East|West|Inner|Outer)?\s*(.*?)\s*(North|South|East|West|Inner|Outer)?$"
        match = re.match(pattern, str(name), re.IGNORECASE)
        if not match: 
            return name, "Centre"
        p_dir, base, s_dir = match.groups()
        return base.strip(), (p_dir or s_dir or "Centre").capitalize()

    