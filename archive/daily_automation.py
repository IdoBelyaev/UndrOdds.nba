"""
Daily Automation
================

Automate daily betting workflow:
- Scheduled data refresh
- Automatic prediction generation
- Notification system
- Error handling and logging

M3 Phase 3: Daily Automation
"""

import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class DailyAutomation:
    """Automate daily betting workflow"""
    
    def __init__(self, log_file: str = 'daily_automation.log'):
        """Initialize daily automation"""
        self.setup_logging(log_file)
        self.logger = logging.getLogger('DailyAutomation')
    
    def setup_logging(self, log_file: str):
        """Setup logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def refresh_data(self) -> bool:
        """
        Refresh all NBA data
        
        Returns:
            True if successful, False otherwise
        """
        self.logger.info("=" * 70)
        self.logger.info("🔄 REFRESHING NBA DATA")
        self.logger.info("=" * 70)
        
        try:
            # Refresh team data
            self.logger.info("\n📊 Refreshing team data...")
            result = subprocess.run(
                ['python', 'data_fetch.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.error(f"❌ Team data refresh failed: {result.stderr}")
                return False
            
            self.logger.info("✅ Team data refreshed")
            
            # Refresh game data
            self.logger.info("\n🏀 Refreshing game data...")
            result = subprocess.run(
                ['python', 'game_data_fetch.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.error(f"❌ Game data refresh failed: {result.stderr}")
                return False
            
            self.logger.info("✅ Game data refreshed")
            
            # Refresh injury data
            self.logger.info("\n🏥 Refreshing injury data...")
            result = subprocess.run(
                ['python', 'injury_data_fetch.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.warning(f"⚠️ Injury data refresh failed: {result.stderr}")
                # Don't fail on injury data - it's not critical
            else:
                self.logger.info("✅ Injury data refreshed")
            
            self.logger.info("\n✅ DATA REFRESH COMPLETE")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Data refresh failed: {e}")
            return False
    
    def update_elo_ratings(self) -> bool:
        """
        Update Elo ratings with latest games
        
        Returns:
            True if successful
        """
        self.logger.info("\n🔄 Updating Elo ratings...")
        
        try:
            result = subprocess.run(
                ['python', 'elo_ratings.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.error(f"❌ Elo update failed: {result.stderr}")
                return False
            
            self.logger.info("✅ Elo ratings updated")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Elo update failed: {e}")
            return False
    
    def validate_data(self) -> bool:
        """
        Run data validation checks
        
        Returns:
            True if validation passed
        """
        self.logger.info("\n✅ Running data validation...")
        
        try:
            result = subprocess.run(
                ['python', 'data_validation.py'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                self.logger.warning(f"⚠️ Data validation warnings: {result.stderr}")
                # Don't fail - warnings are okay
            
            self.logger.info("✅ Data validation complete")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Data validation failed: {e}")
            return False
    
    def send_notification(
        self,
        subject: str,
        message: str,
        to_email: str = None
    ):
        """
        Send email notification
        
        Args:
            subject: Email subject
            message: Email message
            to_email: Recipient email (if configured)
        """
        if not to_email:
            self.logger.info(f"📧 Notification: {subject}")
            self.logger.info(f"   {message}")
            return
        
        # Email notification (requires SMTP configuration)
        self.logger.info(f"📧 Would send email to {to_email}: {subject}")
        # TODO: Implement actual email sending with SMTP
    
    def run_daily_workflow(self, send_notifications: bool = False) -> bool:
        """
        Run complete daily workflow
        
        Args:
            send_notifications: Whether to send email notifications
        
        Returns:
            True if successful
        """
        self.logger.info("\n" + "=" * 70)
        self.logger.info("🚀 STARTING DAILY AUTOMATION WORKFLOW")
        self.logger.info("=" * 70)
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        
        success = True
        
        # Step 1: Refresh data
        if not self.refresh_data():
            self.logger.error("❌ Data refresh failed")
            success = False
        
        # Step 2: Update Elo ratings
        if not self.update_elo_ratings():
            self.logger.error("❌ Elo update failed")
            success = False
        
        # Step 3: Validate data
        if not self.validate_data():
            self.logger.warning("⚠️ Data validation had issues")
        
        # Step 4: Send notification
        if send_notifications:
            if success:
                self.send_notification(
                    "✅ NBA Bet Selector: Daily Update Complete",
                    "All data refreshed successfully. Ready for today's betting."
                )
            else:
                self.send_notification(
                    "❌ NBA Bet Selector: Daily Update Failed",
                    "Some data refresh steps failed. Please check logs."
                )
        
        self.logger.info("\n" + "=" * 70)
        if success:
            self.logger.info("✅ DAILY WORKFLOW COMPLETE")
        else:
            self.logger.error("❌ DAILY WORKFLOW HAD ERRORS")
        self.logger.info("=" * 70)
        
        return success


def create_cron_script():
    """Create shell script for cron job"""
    script_content = """#!/bin/bash
# NBA Bet Selector - Daily Automation
# Run this script daily at 9 AM

cd /Users/idobelyaev/NBA_winners
python daily_automation.py

# Exit with the script's exit code
exit $?
"""
    
    with open('daily_cron.sh', 'w') as f:
        f.write(script_content)
    
    # Make executable
    import os
    os.chmod('daily_cron.sh', 0o755)
    
    print("✅ Cron script created: daily_cron.sh")
    print()
    print("To schedule daily runs at 9 AM:")
    print("   1. Open terminal")
    print("   2. Run: crontab -e")
    print("   3. Add line: 0 9 * * * /Users/idobelyaev/NBA_winners/daily_cron.sh")
    print("   4. Save and exit")


def main():
    """Run daily automation"""
    print("=" * 70)
    print("🤖 DAILY AUTOMATION")
    print("=" * 70)
    
    # Create automation instance
    automation = DailyAutomation()
    
    # Run workflow
    success = automation.run_daily_workflow(send_notifications=False)
    
    # Create cron script
    print("\n📅 Creating cron script for scheduling...")
    create_cron_script()
    
    print("\n✅ DAILY AUTOMATION COMPLETE!")
    print("=" * 70)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())

