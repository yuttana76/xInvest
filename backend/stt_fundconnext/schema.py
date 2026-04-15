import graphene
from graphene_django import DjangoObjectType
from .models import FundProfile, FundPerformance, AssetAllocation, TopHolding
from fundDecision.models import FundAnalysis, AIInsight

class FundAnalysisType(DjangoObjectType):
    class Meta:
        model = FundAnalysis
        fields = "__all__"
        
class AIInsightType(DjangoObjectType):
    class Meta:
        model = AIInsight
        fields = "__all__"

class FundPerformanceType(DjangoObjectType):
    class Meta:
        model = FundPerformance
        fields = "__all__"

class AssetAllocationType(DjangoObjectType):
    class Meta:
        model = AssetAllocation
        fields = "__all__"

class FundProfileType(DjangoObjectType):
    fund_analysis = graphene.List(FundAnalysisType)

    class Meta:
        model = FundProfile
        fields = "__all__"

class TopHoldingType(DjangoObjectType):
    class Meta:
        model = TopHolding
        fields = "__all__"

# class FundProfileTypeByTaxType(DjangoObjectType):
#     fund_analysis = graphene.List(FundAnalysisType)
#     ai_insight = graphene.List(AIInsightType)
#     fund_performance = graphene.List(FundPerformanceType)
#     asset_allocation = graphene.List(AssetAllocationType)

#     class Meta:
#         model = FundProfile
#         fields = "__all__"

#     def resolve_fund_analysis(self, info):
#         return FundAnalysis.objects.filter(fundCode=self.fund_code)
    
#     def resolve_ai_insight(self, info):
#         return AIInsight.objects.filter(fundCode=self.fund_code)
    
#     def resolve_fund_performance(self, info):
#         return FundPerformance.objects.filter(fund_code=self.fund_code)

#     def resolve_asset_allocation(self, info):
#         return AssetAllocation.objects.filter(fund_code=self.fund_code)


class FundProfileTypeByCode(DjangoObjectType):
    fund_analysis = graphene.List(FundAnalysisType)
    ai_insight = graphene.List(AIInsightType)
    fund_performance = graphene.List(FundPerformanceType)
    asset_allocation = graphene.List(AssetAllocationType)
    top_holding = graphene.List(TopHoldingType)

    class Meta:
        model = FundProfile
        fields = "__all__"

    def resolve_fund_analysis(self, info):
        # Return a queryset for multiple rows instead of .first()
        return FundAnalysis.objects.filter(fundCode=self.fund_code)
    
    def resolve_ai_insight(self, info):
        # Return a queryset for multiple rows instead of .first()
        return AIInsight.objects.filter(fundCode=self.fund_code)
    
    def resolve_fund_performance(self, info):
        # Return a queryset for multiple rows instead of .first()
        return FundPerformance.objects.filter(fund_code=self.fund_code)

    def resolve_asset_allocation(self, info):
        # Find the latest available period string ('YYYYMM')
        latest_record = AssetAllocation.objects.filter(fund_code=self.fund_code).order_by('-as_end_of').first()
        if latest_record:
            # Return only the rows matching that latest period
            return AssetAllocation.objects.filter(
                fund_code=self.fund_code,
                as_end_of=latest_record.as_end_of
            )
        return AssetAllocation.objects.none()

    def resolve_top_holding(self, info):
        
        return TopHolding.objects.filter(fund_code=self.fund_code)

class Query(graphene.ObjectType):
    # all_fund_profiles = graphene.List(FundProfileType)
    fund_profile_by_code = graphene.Field(FundProfileTypeByCode, fund_code=graphene.String(required=True))
    fund_profile_by_tax_type = graphene.List(FundProfileType, tax_type=graphene.String(required=True))
    fund_profile_by_fund_policy = graphene.List(FundProfileType, fund_policy=graphene.String(required=True))

    # def resolve_all_fund_profiles(root, info):
    #     return FundProfile.objects.all()

    def resolve_fund_profile_by_code(root, info, fund_code):
        try:
            return FundProfile.objects.get(fund_code=fund_code)
        except FundProfile.DoesNotExist:
            return None

    def resolve_fund_profile_by_tax_type(root, info, tax_type):
        try:
            return FundProfile.objects.filter(tax_type=tax_type)
        except FundProfile.DoesNotExist:
            return None

    def resolve_fund_profile_by_fund_policy(root, info, fund_policy):
        try:
            return FundProfile.objects.filter(fund_policy=fund_policy)
        except FundProfile.DoesNotExist:
            return None

    