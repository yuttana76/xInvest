class PortfolioData {
  final Profile profile;
  final List<MfAccount> mfAccounts;
  final List<PrivateFundAccount> privateFundAccounts;
  final List<BondAccount> bondAccounts;
  final String updatedAt;

  PortfolioData({
    required this.profile,
    required this.mfAccounts,
    required this.privateFundAccounts,
    required this.bondAccounts,
    required this.updatedAt,
  });

  double get totalMfAmount => mfAccounts.fold(0.0, (sum, acc) => sum + acc.balances.fold(0.0, (s, b) => s + b.amount));
  double get totalPfAmount => privateFundAccounts.fold(0.0, (sum, acc) => sum + acc.balances.fold(0.0, (s, b) => s + b.amount));
  double get totalBondAmount => bondAccounts.where((b) => b.status == 'Active').fold(0.0, (sum, b) => sum + b.amount);
  double get totalAmount => totalMfAmount + totalPfAmount + totalBondAmount;

  double get totalMfInvested => mfAccounts.fold(0.0, (sum, acc) => sum + acc.totalInvested);
  double get totalMfProfit => totalMfAmount - totalMfInvested;
  double get mfProfitPercentage => totalMfInvested > 0 ? (totalMfProfit / totalMfInvested) * 100 : 0;

  double get totalPfInvested => privateFundAccounts.fold(0.0, (sum, acc) => sum + acc.totalInvested);
  double get totalPfProfit => totalPfAmount - totalPfInvested;
  double get pfProfitPercentage => totalPfInvested > 0 ? (totalPfProfit / totalPfInvested) * 100 : 0;

  double get totalBondInvested => totalBondAmount; 
  double get totalInvested => totalMfInvested + totalPfInvested + totalBondInvested;

  double get totalProfit => totalAmount - totalInvested;
  double get profitPercentage => totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0;

  double get mfPercentage => totalAmount > 0 ? (totalMfAmount / totalAmount) * 100 : 0;
  double get pfPercentage => totalAmount > 0 ? (totalPfAmount / totalAmount) * 100 : 0;
  double get bondPercentage => totalAmount > 0 ? (totalBondAmount / totalAmount) * 100 : 0;

  factory PortfolioData.fromJson(Map<String, dynamic> json) {
    return PortfolioData(
      profile: Profile.fromJson(json['profile'] ?? {}),
      mfAccounts: (json['mfAccounts'] as List? ?? [])
          .map((i) => MfAccount.fromJson(i))
          .toList(),
      privateFundAccounts: (json['privateFundAccounts'] as List? ?? [])
          .map((i) => PrivateFundAccount.fromJson(i))
          .toList(),
      bondAccounts: (json['bondAccounts'] as List? ?? [])
          .map((i) => BondAccount.fromJson(i))
          .toList(),
      updatedAt: json['updated_at']?.toString() ?? '',
    );
  }
}

class Profile {
  final int id;
  final String fullNameEn;
  final String mobile;
  final String email;

  Profile({
    required this.id,
    required this.fullNameEn,
    required this.mobile,
    required this.email,
  });

  factory Profile.fromJson(Map<String, dynamic> json) {
    return Profile(
      id: (json['id'] as num? ?? 0).toInt(),
      fullNameEn: json['fullNameEn']?.toString() ?? '',
      mobile: json['mobile']?.toString() ?? '',
      email: json['email']?.toString() ?? '',
    );
  }
}

class MfAccount {
  final String accountID;
  final String status;
  final String? marketingName;
  final List<MfBalance> balances;

  MfAccount({
    required this.accountID,
    required this.status,
    this.marketingName,
    required this.balances,
  });

  double get totalAmount => balances.fold(0.0, (sum, b) => sum + b.amount);
  double get totalInvested => balances.fold(0.0, (sum, b) => sum + (b.unitBalance * b.averageCost));
  double get totalProfit => totalAmount - totalInvested;
  double get profitPercentage => totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0;

  factory MfAccount.fromJson(Map<String, dynamic> json) {
    return MfAccount(
      accountID: json['accountID']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      marketingName: json['marketing_name']?.toString(),
      balances: (json['balances'] as List? ?? [])
          .map((i) => MfBalance.fromJson(i))
          .toList(),
    );
  }
}

class MfBalance {
  final String fundCode;
  final double unitBalance;
  final double amount;
  final double averageCost;
  final double nav;
  final String navDate;
  final FundAnalysis? fundAnalysis;

  MfBalance({
    required this.fundCode,
    required this.unitBalance,
    required this.amount,
    required this.averageCost,
    required this.nav,
    required this.navDate,
    this.fundAnalysis,
  });

  double get invested => unitBalance * averageCost;
  double get profit => amount - invested;
  double get profitPercentage => invested > 0 ? (profit / invested) * 100 : 0;

  factory MfBalance.fromJson(Map<String, dynamic> json) {
    return MfBalance(
      fundCode: json['fundCode']?.toString() ?? '',
      unitBalance: (json['unitBalance'] as num? ?? 0).toDouble(),
      amount: (json['amount'] as num? ?? 0).toDouble(),
      averageCost: (json['averageCost'] as num? ?? 0).toDouble(),
      nav: (json['NAV'] as num? ?? 0).toDouble(),
      navDate: json['NAVdate']?.toString() ?? '',
      fundAnalysis: json['fund_analysis'] != null
          ? FundAnalysis.fromJson(json['fund_analysis'])
          : null,
    );
  }
}

class PrivateFundAccount {
  final String accountID;
  final String fundType;
  final String status;
  final List<PrivateFundBalance> balances;

  PrivateFundAccount({
    required this.accountID,
    required this.fundType,
    required this.status,
    required this.balances,
  });

  double get totalAmount => balances.fold(0.0, (sum, b) => sum + b.amount);
  double get totalInvested => balances.fold(0.0, (sum, b) => sum + (b.unitBalance * b.averageCost));
  double get totalProfit => totalAmount - totalInvested;
  double get profitPercentage => totalInvested > 0 ? (totalProfit / totalInvested) * 100 : 0;

  factory PrivateFundAccount.fromJson(Map<String, dynamic> json) {
    return PrivateFundAccount(
      accountID: json['accountID']?.toString() ?? '',
      fundType: json['fundType']?.toString() ?? '',
      status: json['status']?.toString() ?? '',
      balances: (json['privateFundBalances'] as List? ?? [])
          .map((i) => PrivateFundBalance.fromJson(i))
          .toList(),
    );
  }
}

class PrivateFundBalance {
  final String fundCode;
  final double unitBalance;
  final double amount;
  final double averageCost;
  final double nav;
  final String navDate;
  final FundAnalysis? fundAnalysis;

  PrivateFundBalance({
    required this.fundCode,
    required this.unitBalance,
    required this.amount,
    required this.averageCost,
    required this.nav,
    required this.navDate,
    this.fundAnalysis,
  });

  double get invested => unitBalance * averageCost;
  double get profit => amount - invested;
  double get profitPercentage => invested > 0 ? (profit / invested) * 100 : 0;

  factory PrivateFundBalance.fromJson(Map<String, dynamic> json) {
    return PrivateFundBalance(
      fundCode: json['fundCode']?.toString() ?? '',
      unitBalance: (json['unitBalance'] as num? ?? 0).toDouble(),
      amount: (json['amount'] as num? ?? 0).toDouble(),
      averageCost: (json['averageCost'] as num? ?? 0).toDouble(),
      nav: (json['NAV'] as num? ?? 0).toDouble(),
      navDate: json['NAVdate']?.toString() ?? '',
      fundAnalysis: json['fund_analysis'] != null
          ? FundAnalysis.fromJson(json['fund_analysis'])
          : null,
    );
  }
}

class BondAccount {
  final String bondCode;
  final double amount;
  final String status;
  final String fromDate;
  final String toDate;
  final String? issuer;
  final String? bondSymbol;

  BondAccount({
    required this.bondCode,
    required this.amount,
    required this.status,
    required this.fromDate,
    required this.toDate,
    this.issuer,
    this.bondSymbol,
  });

  factory BondAccount.fromJson(Map<String, dynamic> json) {
    return BondAccount(
      bondCode: json['bondCode']?.toString() ?? (json['accountID']?.toString() ?? ''),
      amount: (json['amount'] as num? ?? 0).toDouble(),
      status: json['status']?.toString() ?? '',
      fromDate: json['fromDate']?.toString() ?? '',
      toDate: json['toDate']?.toString() ?? '',
      issuer: json['issuer']?.toString(),
      bondSymbol: json['bondSymbol']?.toString(),
    );
  }
}

class FundAnalysis {
  final double? sentimentScore;
  final String sentimentSummary;
  final String sentimentImpactLevel;

  FundAnalysis({
    this.sentimentScore,
    required this.sentimentSummary,
    required this.sentimentImpactLevel,
  });

  factory FundAnalysis.fromJson(Map<String, dynamic> json) {
    return FundAnalysis(
      sentimentScore: (json['sentiment_score'] as num?)?.toDouble(),
      sentimentSummary: json['sentiment_summary']?.toString() ?? '',
      sentimentImpactLevel: json['sentiment_impact_level']?.toString() ?? '',
    );
  }
}
