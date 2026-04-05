"""
Automated Data Pipeline for NBA Bet Selector
=============================================

This module provides an automated pipeline for:
- Fetching all NBA data sources
- Validating data quality
- Monitoring data freshness
- Error handling and logging
- Daily data refresh

Phase 3: Data Storage & Schemas
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys

# Import our data collection modules
from data_fetch import fetch_team_data
from game_data_fetch import fetch_game_data
from injury_data_fetch import fetch_injury_data
from data_validation import DataValidator
from data_quality_monitor import DataQualityMonitor
from data_consistency_checker import DataConsistencyChecker


class DataPipeline:
    """Automated data pipeline for NBA bet selector"""
    
    def __init__(self, log_level: str = "INFO"):
        """Initialize the data pipeline"""
        self.setup_logging(log_level)
        self.pipeline_status = {
            "timestamp": datetime.now().isoformat(),
            "status": "INITIALIZED",
            "steps": {},
            "errors": [],
            "warnings": []
        }
    
    def setup_logging(self, log_level: str):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data_pipeline.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('DataPipeline')
    
    def run_full_pipeline(self, season: str = "2024-25") -> Dict[str, Any]:
        """
        Run the complete data pipeline
        
        Steps:
        1. Fetch team data
        2. Fetch game data
        3. Fetch injury data
        4. Validate all data
        5. Run quality checks
        6. Run consistency checks
        7. Generate report
        """
        self.logger.info("=" * 70)
        self.logger.info("🚀 STARTING AUTOMATED DATA PIPELINE")
        self.logger.info("=" * 70)
        
        try:
            # Step 1: Fetch team data
            self.logger.info("\n📊 Step 1: Fetching team data...")
            self.fetch_team_data_step(season)
            
            # Step 2: Fetch game data
            self.logger.info("\n🏀 Step 2: Fetching game data...")
            self.fetch_game_data_step(season)
            
            # Step 3: Fetch injury data
            self.logger.info("\n🏥 Step 3: Fetching injury data...")
            self.fetch_injury_data_step(season)
            
            # Step 4: Validate data
            self.logger.info("\n✅ Step 4: Validating data...")
            self.validate_data_step()
            
            # Step 5: Quality checks
            self.logger.info("\n📈 Step 5: Running quality checks...")
            self.quality_check_step()
            
            # Step 6: Consistency checks
            self.logger.info("\n🔄 Step 6: Running consistency checks...")
            self.consistency_check_step()
            
            # Step 7: Generate report
            self.logger.info("\n📋 Step 7: Generating pipeline report...")
            self.generate_report()
            
            self.pipeline_status['status'] = "COMPLETED"
            self.logger.info("\n✅ PIPELINE COMPLETED SUCCESSFULLY")
            
        except Exception as e:
            self.pipeline_status['status'] = "FAILED"
            self.pipeline_status['errors'].append(str(e))
            self.logger.error(f"\n❌ PIPELINE FAILED: {e}")
            raise
        
        finally:
            self.save_pipeline_status()
        
        return self.pipeline_status
    
    def fetch_team_data_step(self, season: str):
        """Step 1: Fetch team data"""
        try:
            self.logger.info(f"   Fetching NBA team stats for {season}...")
            result = fetch_team_data(season)
            
            self.pipeline_status['steps']['team_data'] = {
                "status": "SUCCESS",
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            self.logger.info(f"   ✅ Team data fetched successfully")
            
        except Exception as e:
            self.pipeline_status['steps']['team_data'] = {
                "status": "FAILED",
                "error": str(e)
            }
            self.logger.error(f"   ❌ Failed to fetch team data: {e}")
            raise
    
    def fetch_game_data_step(self, season: str):
        """Step 2: Fetch game data"""
        try:
            self.logger.info(f"   Fetching NBA game data for {season}...")
            result = fetch_game_data(season)
            
            self.pipeline_status['steps']['game_data'] = {
                "status": "SUCCESS",
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            self.logger.info(f"   ✅ Game data fetched successfully")
            
        except Exception as e:
            self.pipeline_status['steps']['game_data'] = {
                "status": "FAILED",
                "error": str(e)
            }
            self.logger.error(f"   ❌ Failed to fetch game data: {e}")
            raise
    
    def fetch_injury_data_step(self, season: str):
        """Step 3: Fetch injury data"""
        try:
            self.logger.info(f"   Fetching NBA injury data for {season}...")
            result = fetch_injury_data(season)
            
            self.pipeline_status['steps']['injury_data'] = {
                "status": "SUCCESS",
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            self.logger.info(f"   ✅ Injury data fetched successfully")
            
        except Exception as e:
            self.pipeline_status['steps']['injury_data'] = {
                "status": "FAILED",
                "error": str(e)
            }
            self.logger.error(f"   ❌ Failed to fetch injury data: {e}")
            # Don't raise - injury data is not critical
            self.pipeline_status['warnings'].append(f"Injury data fetch failed: {e}")
    
    def validate_data_step(self):
        """Step 4: Validate data"""
        try:
            validator = DataValidator()
            results = validator.run_all_validations()
            
            self.pipeline_status['steps']['validation'] = {
                "status": results['overall_status'],
                "timestamp": datetime.now().isoformat(),
                "results": results
            }
            
            if results['overall_status'] == "FAILED":
                self.logger.error("   ❌ Data validation failed")
                raise ValueError("Data validation failed")
            else:
                self.logger.info(f"   ✅ Data validation: {results['overall_status']}")
            
        except Exception as e:
            self.pipeline_status['steps']['validation'] = {
                "status": "FAILED",
                "error": str(e)
            }
            self.logger.error(f"   ❌ Validation step failed: {e}")
            raise
    
    def quality_check_step(self):
        """Step 5: Run quality checks"""
        try:
            monitor = DataQualityMonitor()
            report = monitor.run_all_checks()
            
            self.pipeline_status['steps']['quality_check'] = {
                "status": "SUCCESS",
                "timestamp": datetime.now().isoformat(),
                "quality_score": report['overall_score']
            }
            
            if report['overall_score'] < 60:
                self.pipeline_status['warnings'].append(
                    f"Low quality score: {report['overall_score']}/100"
                )
                self.logger.warning(f"   ⚠️  Low quality score: {report['overall_score']}/100")
            else:
                self.logger.info(f"   ✅ Quality score: {report['overall_score']}/100")
            
        except Exception as e:
            self.pipeline_status['steps']['quality_check'] = {
                "status": "FAILED",
                "error": str(e)
            }
            self.logger.error(f"   ❌ Quality check failed: {e}")
            # Don't raise - quality issues are warnings, not failures
            self.pipeline_status['warnings'].append(f"Quality check failed: {e}")
    
    def consistency_check_step(self):
        """Step 6: Run consistency checks"""
        try:
            checker = DataConsistencyChecker()
            report = checker.run_all_checks()
            
            self.pipeline_status['steps']['consistency_check'] = {
                "status": report['overall_status'],
                "timestamp": datetime.now().isoformat(),
                "issues_count": len(report['issues'])
            }
            
            if report['overall_status'] == "WARNING":
                self.pipeline_status['warnings'].append(
                    f"Consistency issues: {len(report['issues'])} found"
                )
                self.logger.warning(f"   ⚠️  Consistency issues: {len(report['issues'])} found")
            else:
                self.logger.info(f"   ✅ Consistency check passed")
            
        except Exception as e:
            self.pipeline_status['steps']['consistency_check'] = {
                "status": "FAILED",
                "error": str(e)
            }
            self.logger.error(f"   ❌ Consistency check failed: {e}")
            # Don't raise - consistency issues are warnings
            self.pipeline_status['warnings'].append(f"Consistency check failed: {e}")
    
    def generate_report(self):
        """Step 7: Generate pipeline report"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("📊 PIPELINE SUMMARY")
        self.logger.info("=" * 70)
        
        # Count successes
        successful_steps = sum(
            1 for step in self.pipeline_status['steps'].values()
            if step.get('status') in ['SUCCESS', 'PASSED', 'PASSED_WITH_WARNINGS']
        )
        total_steps = len(self.pipeline_status['steps'])
        
        self.logger.info(f"\n✅ Successful Steps: {successful_steps}/{total_steps}")
        self.logger.info(f"⚠️  Warnings: {len(self.pipeline_status['warnings'])}")
        self.logger.info(f"❌ Errors: {len(self.pipeline_status['errors'])}")
        
        if self.pipeline_status['warnings']:
            self.logger.info("\n⚠️  Warnings:")
            for warning in self.pipeline_status['warnings']:
                self.logger.info(f"   • {warning}")
        
        if self.pipeline_status['errors']:
            self.logger.info("\n❌ Errors:")
            for error in self.pipeline_status['errors']:
                self.logger.info(f"   • {error}")
        
        self.logger.info("\n" + "=" * 70)
    
    def save_pipeline_status(self):
        """Save pipeline status to file"""
        filename = f"pipeline_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(self.pipeline_status, f, indent=2)
        
        self.logger.info(f"\n💾 Pipeline status saved to: {filename}")
    
    def quick_refresh(self) -> Dict[str, Any]:
        """
        Quick data refresh without full pipeline
        
        Only fetches new data, skips validation
        Useful for daily updates
        """
        self.logger.info("🔄 Running quick data refresh...")
        
        try:
            # Fetch all data
            self.fetch_team_data_step("2024-25")
            self.fetch_game_data_step("2024-25")
            self.fetch_injury_data_step("2024-25")
            
            self.pipeline_status['status'] = "COMPLETED"
            self.logger.info("✅ Quick refresh completed")
            
        except Exception as e:
            self.pipeline_status['status'] = "FAILED"
            self.pipeline_status['errors'].append(str(e))
            self.logger.error(f"❌ Quick refresh failed: {e}")
            raise
        
        return self.pipeline_status


def main():
    """Run the data pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description='NBA Data Pipeline')
    parser.add_argument(
        '--mode',
        choices=['full', 'quick'],
        default='full',
        help='Pipeline mode: full (with validation) or quick (data only)'
    )
    parser.add_argument(
        '--season',
        default='2024-25',
        help='NBA season (e.g., 2024-25)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level'
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = DataPipeline(log_level=args.log_level)
    
    # Run pipeline
    if args.mode == 'full':
        result = pipeline.run_full_pipeline(season=args.season)
    else:
        result = pipeline.quick_refresh()
    
    # Exit code based on status
    if result['status'] == "FAILED":
        exit(1)
    else:
        exit(0)


if __name__ == "__main__":
    main()

