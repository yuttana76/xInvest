import logging
from celery import shared_task
from datetime import datetime, timedelta
from invest.services.fundconnext import FundConnextService
import os
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def run_daily_fundconnext_etl_trans(business_date_str=None):
    """
    Downloads and processes daily files from FundConnext.
    If business_date_str is None, it defaults to yesterday's date (T-1) in YYYYMMDD format.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext ETL for business date: {business_date_str}")
    fnc_service = FundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process AllottedTransactions
        logger.info(f"Downloading AllottedTransactions for {business_date_str}...")
        try:
            tx_zip_content = fnc_service.download_file(business_date_str, "AllottedTransactions", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/AllottedTransactions.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'AllottedTransactions.zip')
            with open(file_path, 'wb') as f:
                f.write(tx_zip_content)
            logger.info(f"Saved AllottedTransactions to {file_path}")

            logger.info("Processing AllottedTransactions...")
            fnc_service.process_allotted_transactions(tx_zip_content)
        except Exception as e:
            logger.error(f"Failed to process AllottedTransactions: {e}")
            raise e

        logger.info(f"FundConnext ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}

@shared_task
def run_daily_fundconnext_etl_performance_mf_balance(business_date_str=None):
    """
    Downloads and processes daily files from FundConnext.
    If business_date_str is None, it defaults to yesterday's date (T-1) in YYYYMMDD format.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext ETL for business date: {business_date_str}")
    fnc_service = FundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process UnitholderBalance  
        logger.info(f"Downloading UnitholderBalance for {business_date_str}...")
        try:
            bal_zip_content = fnc_service.download_file(business_date_str, "UnitholderBalance", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/UnitholderBalance.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'UnitholderBalance.zip')
            with open(file_path, 'wb') as f:
                f.write(bal_zip_content)
            logger.info(f"Saved UnitholderBalance to {file_path}")

            logger.info("Processing UnitholderBalance...")
            fnc_service.process_unitholder_performance_mf_balance(business_date_str,bal_zip_content)
        except Exception as e:
            logger.error(f"Failed to process UnitholderBalance: {e}")
            raise e

        logger.info(f"FundConnext ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}

@shared_task
def run_daily_fundconnext_etl_current_mf_balance(business_date_str=None):
    """
    Downloads and processes daily files from FundConnext.
    If business_date_str is None, it defaults to yesterday's date (T-1) in YYYYMMDD format.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext ETL for business date: {business_date_str}")
    fnc_service = FundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process CurrentUnitholderBalance  
        logger.info(f"Downloading CurrentUnitholderBalance for {business_date_str}...")
        try:
            bal_zip_content = fnc_service.download_file(business_date_str, "UnitholderBalance", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/CurrentUnitholderBalance.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'CurrentUnitholderBalance.zip')
            with open(file_path, 'wb') as f:
                f.write(bal_zip_content)
            logger.info(f"Saved CurrentUnitholderBalance to {file_path}")

            logger.info("Processing CurrentUnitholderBalance...")
            fnc_service.process_unitholder_current_mf_balance(bal_zip_content)
        except Exception as e:
            logger.error(f"Failed to process CurrentUnitholderBalance: {e}")
            raise e

        logger.info(f"FundConnext ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}

@shared_task
def send_investor_statement_report(investor_id):
    """
    Generates an encrypted statement report PDF and sends it to the investor's email.
    """
    from .models import Investor
    from .services.report_service import ReportService
    
    try:
        investor = Investor.objects.get(id=investor_id)
        logger.info(f"Generating statement report (PDF) for investor: {investor.custCode}")
        
        report_service = ReportService()
        success, message = report_service.send_statement_report(investor)
        
        if success:
            logger.info(f"Successfully sent statement report to {investor.custCode}")
            return {"status": "success", "investor": investor.custCode}
        else:
            logger.error(f"Failed to send statement report for investor {investor.custCode}: {message}")
            return {"status": "error", "message": message}
            
    except Investor.DoesNotExist:
        logger.error(f"Investor with id {investor_id} does not exist")
        return {"status": "error", "message": "Investor not found"}
    except Exception as e:
        logger.error(f"Failed to send statement report for investor {investor_id}: {e}")
        return {"status": "error", "message": str(e)}

