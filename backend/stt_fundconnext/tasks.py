import logging
import os
from celery import shared_task
from datetime import datetime, timedelta
from django.conf import settings
from .services import STTFundConnextService

logger = logging.getLogger(__name__)

@shared_task
def run_daily_fundconnext_etl_fund_profile(business_date_str=None):
    """
    Downloads and processes FundProfile from FundConnext.
    If business_date_str is None, it defaults to yesterday's date (T-1) in YYYYMMDD format.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext FundProfile ETL for business date: {business_date_str}")
    fnc_service = STTFundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process FundProfile  
        logger.info(f"Downloading FundProfile for {business_date_str}...")
        try:
            profile_zip_content = fnc_service.download_file(business_date_str, "FundProfile", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/FundProfile.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'FundProfile.zip')
            with open(file_path, 'wb') as f:
                f.write(profile_zip_content)
            logger.info(f"Saved FundProfile to {file_path}")

            logger.info("Processing FundProfile...")
            fnc_service.process_fund_profile(profile_zip_content)
        except Exception as e:
            logger.error(f"Failed to process FundProfile: {e}")
            raise e

        logger.info(f"FundConnext FundProfile ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext FundProfile ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}

@shared_task
def run_daily_fundconnext_etl_fund_performance(business_date_str=None):
    """
    Downloads and processes Fund Performance from FundConnext.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext ETL for FundPerformance: {business_date_str}")
    fnc_service = STTFundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process FundPerformance  
        logger.info(f"Downloading FundPerformance for {business_date_str}...")
        try:
            perf_zip_content = fnc_service.download_file(business_date_str, "FundPerformance", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/FundPerformance.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'FundPerformance.zip')
            with open(file_path, 'wb') as f:
                f.write(perf_zip_content)
            logger.info(f"Saved FundPerformance to {file_path}")

            logger.info("Processing FundPerformance...")
            fnc_service.process_fund_performance(perf_zip_content)
        except Exception as e:
            logger.error(f"Failed to process FundPerformance: {e}")
            raise e

        logger.info(f"FundConnext FundPerformance ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext FundPerformance ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}

@shared_task
def run_daily_fundconnext_etl_asset_allocation(business_date_str=None):
    """
    Downloads and processes Asset Allocation from FundConnext.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext ETL for AssetAllocation: {business_date_str}")
    fnc_service = STTFundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process AssetAllocation  
        logger.info(f"Downloading AssetAllocation for {business_date_str}...")
        try:
            zip_content = fnc_service.download_file(business_date_str, "AssetAllocation", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/AssetAllocation.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'AssetAllocation.zip')
            with open(file_path, 'wb') as f:
                f.write(zip_content)
            logger.info(f"Saved AssetAllocation to {file_path}")

            logger.info("Processing AssetAllocation...")
            fnc_service.process_asset_allocation(zip_content)
        except Exception as e:
            logger.error(f"Failed to process AssetAllocation: {e}")
            raise e

        logger.info(f"FundConnext AssetAllocation ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext AssetAllocation ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}

@shared_task
def run_daily_fundconnext_etl_top_holding(business_date_str=None):
    """
    Downloads and processes Top Holding from FundConnext.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext ETL for TopHolding: {business_date_str}")
    fnc_service = STTFundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process TopHolding
        logger.info(f"Downloading TopHolding for {business_date_str}...")
        try:
            zip_content = fnc_service.download_file(business_date_str, "TopHolding", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/TopHolding.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'TopHolding.zip')
            with open(file_path, 'wb') as f:
                f.write(zip_content)
            logger.info(f"Saved TopHolding to {file_path}")

            logger.info("Processing TopHolding...")
            fnc_service.process_top_holding(zip_content)
        except Exception as e:
            logger.error(f"Failed to process TopHolding: {e}")
            raise e

        logger.info(f"FundConnext TopHolding ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext TopHolding ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}


@shared_task
def run_daily_fundconnext_etl_customer_individual(business_date_str=None):
    """
    Downloads and processes CustomerProfile (Individual) from FundConnext.
    """
    if business_date_str is None:
        business_date = datetime.now() - timedelta(days=1)
        business_date_str = business_date.strftime('%Y%m%d')

    logger.info(f"Starting FundConnext ETL for CustomerIndividual: {business_date_str}")
    fnc_service = STTFundConnextService()

    try:
        # Step 1: Login to get token
        logger.info("Authenticating with FundConnext...")
        token = fnc_service.login()

        # Step 2: Download and process CustomerProfile
        logger.info(f"Downloading CustomerProfile for {business_date_str}...")
        try:
            zip_content = fnc_service.download_file(business_date_str, "CustomerProfile", token)
            
            # Save zip file to logs/fundconnext/YYYYMMDD/CustomerProfile.zip
            log_dir = os.path.join(settings.BASE_DIR, 'logs', 'fundconnext', business_date_str)
            os.makedirs(log_dir, exist_ok=True)
            file_path = os.path.join(log_dir, 'CustomerProfile.zip')
            with open(file_path, 'wb') as f:
                f.write(zip_content)
            logger.info(f"Saved CustomerProfile to {file_path}")

            logger.info("Processing CustomerProfile...")
            fnc_service.process_customer_individual(zip_content)
        except Exception as e:
            logger.error(f"Failed to process CustomerProfile: {e}")
            raise e

        logger.info(f"FundConnext CustomerIndividual ETL completed successfully for {business_date_str}")
        return {"status": "success", "business_date": business_date_str}

    except Exception as e:
        logger.error(f"FundConnext CustomerIndividual ETL process failed: {e}")
        return {"status": "error", "message": str(e), "business_date": business_date_str}
@shared_task
def sync_fundconnext_individual_profile(card_number):
    """
    Syncs a single customer profile from FundConnext.
    """
    logger.info(f"Starting async sync for card: {card_number}")
    fnc_service = STTFundConnextService()
    try:
        profile_data = fnc_service.get_api_customer_individual_investor_profile_v5(card_number)
        
        # Sync to local database
        # If we get here, profile_data is the JSON from FundConnext
        # The API usually returns a list or a single dict
        items = profile_data if isinstance(profile_data, list) else [profile_data]
        for item in items:
            fnc_service.sync_customer_individual(item)
        
        logger.info(f"Async sync completed for card: {card_number}")
        return {"status": "success", "card_number": card_number}
    except Exception as e:
        logger.error(f"Async sync failed for card {card_number}: {e}")
        return {"status": "error", "message": str(e), "card_number": card_number}
