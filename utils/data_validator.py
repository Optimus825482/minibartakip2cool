"""
Data Validation Tool
Migration sonrası veri bütünlüğünü kontrol eder
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Tuple
import hashlib


class DataValidator:
    """Migration sonrası veri doğrulama"""
    
    def __init__(self, mysql_url: str, postgres_url: str):
        self.mysql_url = mysql_url
        self.postgres_url = postgres_url
        
        self.mysql_engine = create_engine(mysql_url)
        self.postgres_engine = create_engine(postgres_url)
        
        MySQLSession = sessionmaker(bind=self.mysql_engine)
        PostgresSession = sessionmaker(bind=self.postgres_engine)
        
        self.mysql_session = MySQLSession()
        self.postgres_session = PostgresSession()
        
        self.validation_results = {
            'row_count_matches': [],
            'row_count_mismatches': [],
            'foreign_key_issues': [],
            'orphan_records': []
        }
    
    def validate_row_counts(self, table_name: str) -> Tuple[bool, int, int]:
        """Tablo kayıt sayılarını karşılaştır"""
        mysql_count = self.mysql_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()
        
        postgres_count = self.postgres_session.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        ).scalar()
        
        matches = mysql_count == postgres_count
        
        if matches:
            self.validation_results['row_count_matches'].append({
                'table': table_name,
                'count': mysql_count
            })
        else:
            self.validation_results['row_count_mismatches'].append({
                'table': table_name,
                'mysql_count': mysql_count,
                'postgres_count': postgres_count,
                'difference': abs(mysql_count - postgres_count)
            })
        
        return matches, mysql_count, postgres_count
    
    def validate_foreign_keys(self, table_name: str, fk_column: str, ref_table: str) -> List[Dict]:
        """Foreign key ilişkilerini kontrol et"""
        query = text(f"""
            SELECT {fk_column} 
            FROM {table_name} 
            WHERE {fk_column} IS NOT NULL 
            AND {fk_column} NOT IN (SELECT id FROM {ref_table})
        """)
        
        orphans = self.postgres_session.execute(query).fetchall()
        
        if orphans:
            self.validation_results['orphan_records'].append({
                'table': table_name,
                'fk_column': fk_column,
                'ref_table': ref_table,
                'orphan_count': len(orphans)
            })
        
        return [dict(row._mapping) for row in orphans]
    
    def validate_all(self, tables: List[str]) -> Dict:
        """Tüm tabloları doğrula"""
        print("\n" + "="*60)
        print("🔍 Starting Data Validation")
        print("="*60)
        
        for table in tables:
            print(f"\n📊 Validating: {table}")
            
            # Row count validation
            matches, mysql_count, postgres_count = self.validate_row_counts(table)
            
            if matches:
                print(f"   ✅ Row counts match: {mysql_count}")
            else:
                print(f"   ❌ Row count mismatch!")
                print(f"      MySQL: {mysql_count}")
                print(f"      PostgreSQL: {postgres_count}")
        
        # Summary
        print("\n" + "="*60)
        print("📊 Validation Summary")
        print("="*60)
        print(f"Tables validated: {len(tables)}")
        print(f"Row count matches: {len(self.validation_results['row_count_matches'])}")
        print(f"Row count mismatches: {len(self.validation_results['row_count_mismatches'])}")
        print(f"Orphan records found: {len(self.validation_results['orphan_records'])}")
        
        is_valid = (
            len(self.validation_results['row_count_mismatches']) == 0 and
            len(self.validation_results['orphan_records']) == 0
        )
        
        print(f"\n{'✅ Validation passed!' if is_valid else '❌ Validation failed!'}")
        
        return {
            'is_valid': is_valid,
            'results': self.validation_results
        }
    
    def close(self):
        """Bağlantıları kapat"""
        self.mysql_session.close()
        self.postgres_session.close()
        self.mysql_engine.dispose()
        self.postgres_engine.dispose()
