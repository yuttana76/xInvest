import io
import zipfile
import logging
from decimal import Decimal
from datetime import datetime
from django.db import transaction

from invest.services.fundconnext import FundConnextService
from .models import FundProfile

logger = logging.getLogger(__name__)

class STTFundConnextService(FundConnextService):

    def process_fund_profile(self, zip_content):
        logger.info('* Welcome to Fund Profile ETL')
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                content = f.read().decode('utf-8-sig', errors='replace')
                
        lines = content.splitlines()
        profiles_to_create = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('202') or line.startswith('Detail'):
                if len(line.split('|')) < 10:
                    continue
                if "Fund Code" in line or "fund_code" in line.lower():
                    continue

            parts = line.split('|')
            if len(parts) < 63:
                continue

            # Safe int parsing
            def safe_int(val):
                if not val or not val.strip():
                    return None
                try:
                    return int(float(val.strip().replace(',', '')))
                except (ValueError, TypeError):
                    return None

            fp = FundProfile(
                fund_code=parts[0].strip(),
                amc_code=parts[1].strip(),
                fund_name_th=parts[2].strip()[:500],
                fund_name_en=parts[3].strip()[:500],
                fund_policy=parts[4].strip()[:1],
                tax_type=parts[5].strip()[:10],
                fif_flag=parts[6].strip()[:1],
                dividend_flag=parts[7].strip()[:1],
                registration_date=self.safe_date(parts[8]),
                fund_risk_level=parts[9].strip()[:2],
                fx_risk_flag=parts[10].strip()[:1],
                fatca_allow_flag=parts[11].strip()[:1],
                buy_cut_off_time=parts[12].strip()[:4],
                fst_lowbuy_val=self.safe_decimal(parts[13]),
                nxt_lowbuy_val=self.safe_decimal(parts[14]),
                sell_cut_off_time=parts[15].strip()[:4],
                lowsell_val=self.safe_decimal(parts[16]),
                lowsell_unit=self.safe_decimal(parts[17]),
                lowbal_val=self.safe_decimal(parts[18]),
                lowbal_unit=self.safe_decimal(parts[19]),
                sell_settlement_day=safe_int(parts[20]),
                switching_settlement_day=safe_int(parts[21]),
                switch_out_flag=parts[22].strip()[:1],
                switch_in_flag=parts[23].strip()[:1],
                fund_class=parts[24].strip()[:30],
                buy_period_flag=parts[25].strip()[:1],
                sell_period_flag=parts[26].strip()[:1],
                switch_in_period_flag=parts[27].strip()[:1],
                switch_out_period_flag=parts[28].strip()[:1],
                buy_pre_order_day=safe_int(parts[29]),
                sell_pre_order_day=safe_int(parts[30]),
                switch_pre_order_day=safe_int(parts[31]),
                auto_redeem_fund=parts[32].strip()[:300],
                beg_ipo_date=self.safe_date(parts[33]),
                end_ipo_date=self.safe_date(parts[34]),
                plain_complex_fund=parts[35].strip()[:1],
                derivatives_flag=parts[36].strip()[:1],
                lag_allocation_day=safe_int(parts[37]),
                settlement_holiday_flag=parts[38].strip()[:1],
                health_insurance=parts[39].strip()[:1],
                previous_fund_code=parts[40].strip()[:30],
                investor_alert=parts[41].strip()[:20],
                isin=parts[42].strip()[:15],
                lowbal_condition=parts[43].strip()[:1],
                project_retail_type=parts[44].strip()[:1],
                fund_compare_performance_description=parts[45].strip()[:100],
                allocate_digit=safe_int(parts[46]),
                etf_flag=parts[47].strip()[:1],
                trustee=parts[48].strip()[:1000],
                registrar=parts[49].strip()[:1000],
                register_id=parts[50].strip()[:15],
                lmts_notice_period_amount=parts[51].strip()[:200],
                lmts_notice_period_percent_aum=parts[52].strip()[:200],
                lmts_adls_amount=parts[53].strip()[:200],
                lmts_adls_percent_aum=parts[54].strip()[:200],
                lmts_liquidity_fee_amount=parts[55].strip()[:200],
                lmts_liquidity_fee_percent_aum=parts[56].strip()[:200],
                other_information_url=parts[57].strip()[:200],
                currency=parts[58].strip()[:3],
                complex_fund_presentation=parts[59].strip()[:200],
                risk_acknowledgement_of_complex_fund=parts[60].strip()[:200],
                redemption_type_condition=parts[61].strip()[:4],
                internal_use=parts[62].strip()[:1]
            )
            profiles_to_create.append(fp)

        if profiles_to_create:
            with transaction.atomic():
                FundProfile.objects.all().delete()
                FundProfile.objects.bulk_create(profiles_to_create, ignore_conflicts=True)
            logger.info(f"Successfully processed {len(profiles_to_create)} Fund Profiles.")
        else:
            logger.info("Parsing finished, but 0 brand new fund profiles were created.")

    def process_fund_performance(self, zip_content):
        from stt_fundconnext.models import FundPerformance
        logger.info('* Welcome to Fund Performance')
        
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                content = f.read().decode('utf-8-sig', errors='replace')
        
        lines = content.splitlines()
        performances_to_create = []

        for line in lines:
            line = line.strip()
            if not line or (line.startswith('202') and len(line.split('|')) < 5):
                continue
            
            parts = line.split('|')
            if len(parts) < 20:
                continue
            
            fund_code_val = parts[0].strip()
            nav_date_val = parts[13].strip()

            if not fund_code_val or not nav_date_val:
                continue

            perf = FundPerformance(
                fund_code=fund_code_val,
                p_ytd_return=self.safe_decimal(parts[1]),
                p_3m_return=self.safe_decimal(parts[2]),
                p_6m_return=self.safe_decimal(parts[3]),
                p_1y_return=self.safe_decimal(parts[4]),
                p_3y_return=self.safe_decimal(parts[5]),
                p_5y_return=self.safe_decimal(parts[6]),
                p_10y_return=self.safe_decimal(parts[7]),
                p_si_return=self.safe_decimal(parts[8]),
                p_1y_sd=self.safe_decimal(parts[9]),
                p_3y_sd=self.safe_decimal(parts[10]),
                p_5y_sd=self.safe_decimal(parts[11]),
                p_10y_sd=self.safe_decimal(parts[12]),
                nav_date=self.safe_date(nav_date_val),
                p_1m_return=self.safe_decimal(parts[14]),
                p_1w_return=self.safe_decimal(parts[15]),
                max_dd_1y=self.safe_decimal(parts[16]),
                max_dd_3y=self.safe_decimal(parts[17]),
                max_dd_5y=self.safe_decimal(parts[18]),
                max_dd_10y=self.safe_decimal(parts[19]),
            )
            # Make sure nav_date is parsed successfully
            if perf.nav_date:
                performances_to_create.append(perf)

        if performances_to_create:
            with transaction.atomic():
                target_fund_codes = [p.fund_code for p in performances_to_create]
                target_nav_dates = [p.nav_date for p in performances_to_create]
                
                FundPerformance.objects.filter(
                    fund_code__in=target_fund_codes,
                    nav_date__in=target_nav_dates
                ).delete()

                FundPerformance.objects.bulk_create(performances_to_create, ignore_conflicts=True)
                
            logger.info(f"Successfully processed {len(performances_to_create)} Fund Performances.")
        else:
            logger.info("Parsing finished, but 0 brand new performances were created.")

    def process_asset_allocation(self, zip_content):
        from stt_fundconnext.models import AssetAllocation
        logger.info('* Welcome to Asset Allocation')
        
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                content = f.read().decode('utf-8-sig', errors='replace')
        
        lines = content.splitlines()
        allocations_to_create = []

        for line in lines:
            line = line.strip()
            if not line or (line.startswith('202') and len(line.split('|')) < 3):
                continue
            
            parts = line.split('|')
            if len(parts) < 4:
                continue
            
            fund_code_val = parts[0].strip()
            investment_type_code_val = parts[1].strip()
            as_end_of_val = parts[2].strip()

            if not fund_code_val or not investment_type_code_val or not as_end_of_val:
                continue

            alloc = AssetAllocation(
                fund_code=fund_code_val,
                investment_type_code=investment_type_code_val,
                as_end_of=as_end_of_val,
                investment_size=self.safe_decimal(parts[3])
            )
            allocations_to_create.append(alloc)

        if allocations_to_create:
            with transaction.atomic():
                target_fund_codes = [a.fund_code for a in allocations_to_create]
                target_investment_type_codes = [a.investment_type_code for a in allocations_to_create]
                target_as_end_of = [a.as_end_of for a in allocations_to_create]
                
                # Delete existing records with the same fund_code, investment_type_code, and as_end_of
                AssetAllocation.objects.filter(
                    fund_code__in=target_fund_codes,
                    investment_type_code__in=target_investment_type_codes,
                    as_end_of__in=target_as_end_of
                ).delete()

                # Create new records
                AssetAllocation.objects.bulk_create(allocations_to_create, ignore_conflicts=True)
                
            logger.info(f"Successfully processed {len(allocations_to_create)} Asset Allocations.")
        else:
            logger.info("Parsing finished, but 0 brand new asset allocations were created.")

    def process_top_holding(self, zip_content):
        from stt_fundconnext.models import TopHolding
        logger.info('* Welcome to Top Holding')
        
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            filename = z.namelist()[0]
            with z.open(filename) as f:
                content = f.read().decode('utf-8-sig', errors='replace')
        
        lines = content.splitlines()
        holdings_to_create = []

        for line in lines:
            line = line.strip()
            if not line or (line.startswith('202') and len(line.split('|')) < 5):
                continue
            
            parts = line.split('|')
            if len(parts) < 6:
                continue
            
            fund_code_val = parts[0].strip()
            securities_seq_val = parts[1].strip()
            as_end_of_val = parts[4].strip()

            if not fund_code_val or not securities_seq_val or not as_end_of_val:
                continue

            # Safe int parsing for securities_seq
            def safe_int(val):
                if not val or not val.strip():
                    return None
                try:
                    return int(float(val.strip().replace(',', '')))
                except (ValueError, TypeError):
                    return None

            holding = TopHolding(
                fund_code=fund_code_val,
                securities_seq=safe_int(securities_seq_val),
                securities_name=parts[2].strip()[:200],
                securities_abbreviation_name=parts[3].strip()[:50] if parts[3].strip() else None,
                as_end_of=as_end_of_val,
                securities_invest_size=self.safe_decimal(parts[5])
            )
            if holding.securities_seq is not None:
                holdings_to_create.append(holding)

        if holdings_to_create:
            with transaction.atomic():
                target_fund_codes = list(set([h.fund_code for h in holdings_to_create]))
                target_as_end_of = list(set([h.as_end_of for h in holdings_to_create]))
                
                # Delete existing records for the same fund codes and time periods
                TopHolding.objects.filter(
                    fund_code__in=target_fund_codes,
                    as_end_of__in=target_as_end_of
                ).delete()

                # Create new records
                TopHolding.objects.bulk_create(holdings_to_create, ignore_conflicts=True)
                

    def process_customer_individual(self, zip_content):
        import json
        from stt_fundconnext.models import CustomerIndividual
        from invest.models import Investor, InvestorAccount
        logger.info('* Welcome to Customer Individual ETL (JSON)')
        
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            # filter file name  like 20260409_MPS_INDIVIDUAL.json
            filename = [f for f in z.namelist() if f.endswith('_INDIVIDUAL.json')][0]
            with z.open(filename) as f:
                # FundConnext JSON files are usually UTF-8
                data = json.loads(f.read().decode('utf-8-sig', errors='replace'))
        
        if not isinstance(data, list):
            data = [data]
            
        count_updated = 0
        count_created = 0

        for item in data:
            card_number = item.get('cardNumber')
            if not card_number:
                continue
            
            # Map JSON keys to model fields
            defaults = {
                'identification_card_type': item.get('identificationCardType'),
                'card_expiry_date': item.get('cardExpiryDate'),
                'accompanying_document': item.get('accompanyingDocument'),
                'title': item.get('title'),
                'title_other': item.get('titleOther'),
                'en_first_name': item.get('enFirstName'),
                'en_last_name': item.get('enLastName'),
                'th_first_name': item.get('thFirstName'),
                'th_last_name': item.get('thLastName'),
                'birth_date': item.get('birthDate'),
                'nationality': item.get('nationality'),
                'mobile_number': item.get('mobileNumber'),
                'email': item.get('email'),
                'phone': item.get('phone'),
                'fax': item.get('fax'),
                'marital_status': item.get('maritalStatus'),
                'spouse': item.get('spouse'),
                'occupation_id': item.get('occupationId'),
                'occupation_other': item.get('occupationOther'),
                'business_type_id': item.get('businessTypeId'),
                'business_type_other': item.get('businessTypeOther'),
                'company_name': item.get('companyName'),
                'work_position': item.get('workPosition'),
                'monthly_income_level': item.get('monthlyIncomeLevel'),
                'asset_value': item.get('assetValue'),
                'income_source': item.get('incomeSource'),
                'income_source_other': item.get('incomeSourceOther'),
                'income_source_country': item.get('incomeSourceCountry'),
                'related_political_person': bool(item.get('relatedPoliticalPerson')),
                'political_related_person_position': item.get('politicalRelatedPersonPosition'),
                'can_accept_fx_risk': bool(item.get('canAcceptFxRisk')),
                'can_accept_derivative_investment': bool(item.get('canAcceptDerivativeInvestment')),
                'suitability_risk_level': item.get('suitabilityRiskLevel'),
                'suitability_evaluation_date': item.get('suitabilityEvaluationDate'),
                'fatca': bool(item.get('fatca')),
                'fatca_declaration_date': item.get('fatcaDeclarationDate'),
                'cdd_score': item.get('cddScore'),
                'cdd_date': item.get('cddDate'),
                'referral_person': item.get('referralPerson'),
                'application_date': item.get('applicationDate'),
                'accepted_by': item.get('acceptedBy'),
                'open_fund_connext_form_flag': item.get('openFundConnextFormFlag'),
                'approved_date': item.get('approvedDate'),
                'approved_date_time': item.get('approvedDateTime'),
                'open_channel': item.get('openChannel'),
                'investor_class': item.get('investorClass'),
                'vulnerable_flag': bool(item.get('vulnerableFlag')),
                'vulnerable_detail': item.get('vulnerableDetail'),
                'ndid_flag': bool(item.get('ndidFlag')),
                'ndid_request_id': item.get('ndidRequestId'),
                'investor_type': item.get('investorType'),
                'knowledge_assessment_result': bool(item.get('knowledgeAssessmentResult')),
                'profile_status': item.get('profileStatus'),
                'crs_place_of_birth_country': item.get('crsPlaceOfBirthCountry'),
                'crs_place_of_birth_city': item.get('crsPlaceOfBirthCity'),
                'crs_tax_residence_in_countries_other_than_the_us': bool(item.get('crsTaxResidenceInCountriesOtherThanTheUS')),
                'crs_declaration_date': item.get('crsDeclarationDate'),
                'identity_verification_date_time': item.get('identityVerificationDateTime'),
                'dopa_verification_date_time': item.get('dopaVerificationDateTime'),
                'current_address_same_as_flag': item.get('currentAddressSameAsFlag'),
                # JSONFields
                'identification_document': item.get('identificationDocument'),
                'current_address': item.get('current'),
                'work_address': item.get('work'),
                'suitability_form': item.get('suitabilityForm'),
                'knowledge_assessment_form': item.get('knowledgeAssessmentForm'),
                'crs_details': item.get('crsDetails'),
                'accounts': item.get('accounts'),
            }

            obj, created = CustomerIndividual.objects.update_or_create(
                card_number=card_number,
                defaults=defaults
            )
            if created:
                count_created += 1
            else:
                count_updated += 1

        # # Sync to InvestorAccount in invest app
        # investors = Investor.objects.filter(custCode__in=[item.get('cardNumber') for item in data if item.get('cardNumber')])
        # investor_map = {inv.custCode: inv for inv in investors}

        # count_acc_updated = 0
        # count_acc_created = 0

        # for item in data:
        #     card_number = item.get('cardNumber')
        #     investor = investor_map.get(card_number)
        #     if not investor:
        #         continue
            
        #     accounts_data = item.get('accounts', [])
        #     for acc in accounts_data:
        #         acc_id = acc.get('accountId')
        #         if not acc_id:
        #             continue
                
        #         # Parse approvedDateTime as openDate
        #         open_date = None
        #         approved_dt_str = acc.get('approvedDateTime')
        #         if approved_dt_str and len(approved_dt_str) >= 8:
        #             try:
        #                 open_date = datetime.strptime(approved_dt_str[:8], "%Y%m%d").date()
        #             except ValueError:
        #                 pass
                
        #         # Map status
        #         status_raw = acc.get('accountStatus', 'Active').capitalize()
        #         # Ensure it's either Active or Inactive
        #         status_val = 'Active' if status_raw == 'Active' else 'Inactive'

        #         acc_obj, acc_created = InvestorAccount.objects.update_or_create(
        #             compCode=investor.compCode,
        #             accountID=acc_id,
        #             defaults={
        #                 'custCode': investor,
        #                 'openDate': open_date,
        #                 'icLicense': acc.get('icLicense'),
        #                 'status': status_val,
        #             }
        #         )
        #         if acc_created:
        #             count_acc_created += 1
        #         else:
        #             count_acc_updated += 1

        logger.info(f"Successfully processed Customer Individuals: {count_created} created, {count_updated} updated.")
        # if count_acc_created > 0 or count_acc_updated > 0:
        #     logger.info(f"InvestorAccount Sync: {count_acc_created} created, {count_acc_updated} updated.")
