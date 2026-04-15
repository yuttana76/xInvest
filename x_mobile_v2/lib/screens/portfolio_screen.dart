import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../services/portfolio_service.dart';
import '../models/portfolio.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';

class PortfolioScreen extends StatefulWidget {
  const PortfolioScreen({super.key});

  @override
  State<PortfolioScreen> createState() => _PortfolioScreenState();
}

class _PortfolioScreenState extends State<PortfolioScreen> {
  final PortfolioService _portfolioService = PortfolioService();
  bool _isLoading = true;
  PortfolioData? _portfolioData;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final data = await _portfolioService.getPortfolioInfo();
    if (mounted) {
      setState(() {
        _portfolioData = data;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _portfolioData == null
              ? const Center(child: Text('Failed to load portfolio'))
              : CustomScrollView(
                  slivers: [
                    SliverAppBar(
                      backgroundColor: AppTheme.backgroundDark,
                      expandedHeight: 120,
                      floating: true,
                      pinned: true,
                      flexibleSpace: FlexibleSpaceBar(
                        title: Text(
                          'Portfolio',
                          style: GoogleFonts.manrope(
                            fontWeight: FontWeight.w800,
                            color: AppTheme.textPrimary,
                            letterSpacing: -1,
                          ),
                        ),
                        titlePadding: const EdgeInsets.only(left: 24, bottom: 16),
                        background: Container(color: AppTheme.backgroundDark),
                      ),
                      actions: [
                        IconButton(
                          onPressed: _loadData,
                          icon: const Icon(Icons.refresh, color: AppTheme.primaryEmerald),
                        ),
                        IconButton(
                          onPressed: () {},
                          icon: const Icon(Icons.more_vert, color: AppTheme.primaryEmerald),
                        ),
                        const SizedBox(width: 8),
                      ],
                    ),
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'As of ${DateFormat('EEEE, MMMM d, yyyy').format(DateTime.now())}',
                              style: GoogleFonts.inter(
                                fontSize: 13,
                                color: AppTheme.textSecondary,
                              ),
                            ),
                            const SizedBox(height: 24),
                            _buildAssetAllocation(),
                          ],
                        ),
                      ),
                    ),
                    if (_portfolioData!.mfAccounts.isNotEmpty)
                      _buildProductSection(
                        'Mutual Funds',
                        _buildMfAccounts(),
                        totalAmount: _portfolioData!.totalMfAmount,
                        profit: _portfolioData!.totalMfProfit,
                        profitPercentage: _portfolioData!.mfProfitPercentage,
                      ),
                    if (_portfolioData!.privateFundAccounts.isNotEmpty)
                      _buildProductSection(
                        'Private Funds',
                        _buildPfAccounts(),
                        totalAmount: _portfolioData!.totalPfAmount,
                        profit: _portfolioData!.totalPfProfit,
                        profitPercentage: _portfolioData!.pfProfitPercentage,
                      ),
                    if (_portfolioData!.bondAccounts.isNotEmpty)
                      _buildProductSection('Bonds', _buildBondAccounts(), totalAmount: _portfolioData!.totalBondAmount),
                    const SliverToBoxAdapter(child: SizedBox(height: 40)),
                  ],
                ),
    );
  }

  Widget _buildProductSection(String title, List<Widget> children, {double? totalAmount, double? profit, double? profitPercentage}) {
    // final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);
    final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);


    return SliverPadding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
      sliver: SliverList(
        delegate: SliverChildListDelegate([
          Padding(
            padding: const EdgeInsets.only(bottom: 16.0),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  title,
                  style: GoogleFonts.manrope(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimary,
                  ),
                ),
                if (totalAmount != null)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        currencyFormat.format(totalAmount),
                        style: GoogleFonts.manrope(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: AppTheme.textPrimary,
                        ),
                      ),
                      if (profit != null && profitPercentage != null)
                        Text(
                          '${profit >= 0 ? '+' : ''}${currencyFormat.format(profit)} (${profitPercentage.toStringAsFixed(2)}%)',
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: profit >= 0 ? AppTheme.accentGreen : Colors.redAccent,
                          ),
                        ),
                    ],
                  ),
              ],
            ),
          ),
          ...children,
        ]),
      ),
    );
  }

  List<Widget> _buildMfAccounts() {
    return _portfolioData!.mfAccounts.map((account) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAccountHeader(
            account.accountID,
            amount: account.totalAmount,
            profit: account.totalProfit,
            profitPercentage: account.profitPercentage,
          ),
          ...account.balances.map((balance) => _buildInvestmentItem(
                name: balance.fundCode,
                detail: 'Units: ${balance.unitBalance.toStringAsFixed(4)}',
                amount: balance.amount,
                nav: balance.nav,
                profit: balance.profit,
                profitPercentage: balance.profitPercentage,
                sentimentScore: balance.fundAnalysis?.sentimentScore,
                sentiment: balance.fundAnalysis?.sentimentImpactLevel,
              )),
          const SizedBox(height: 16),
        ],
      );
    }).toList();
  }

  List<Widget> _buildPfAccounts() {
    return _portfolioData!.privateFundAccounts.map((account) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildAccountHeader(
            account.accountID,
            subTitle: account.fundType,
            amount: account.totalAmount,
            profit: account.totalProfit,
            profitPercentage: account.profitPercentage,
          ),
          ...account.balances.map((balance) => _buildInvestmentItem(
                name: balance.fundCode,
                detail: 'NAV: ${balance.nav.toStringAsFixed(2)}',
                amount: balance.amount,
                nav: balance.nav,
                profit: balance.profit,
                profitPercentage: balance.profitPercentage,
                sentimentScore: balance.fundAnalysis?.sentimentScore,
                sentiment: balance.fundAnalysis?.sentimentImpactLevel,
              )),
          const SizedBox(height: 16),
        ],
      );
    }).toList();
  }

  List<Widget> _buildBondAccounts() {
    return _portfolioData!.bondAccounts
        .where((bond) => bond.status == 'Active')
        .map((bond) {
      return _buildInvestmentItem(
        name: bond.bondCode,
        detail: 'Due: ${bond.toDate.split('T')[0]}',
        amount: bond.amount,
        status: bond.status,
      );
    }).toList();
  }

  Widget _buildAccountHeader(String accountID, {String? subTitle, double? amount, double? profit, double? profitPercentage}) {
    // final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);
    final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);

    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0, top: 8.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(Icons.account_balance_outlined, size: 16, color: AppTheme.accentGreen),
                  const SizedBox(width: 8),
                  Text(
                    'Account: $accountID',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.accentGreen,
                    ),
                  ),
                ],
              ),
              if (amount != null)
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      currencyFormat.format(amount),
                      style: GoogleFonts.manrope(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    if (profit != null && profitPercentage != null)
                      Text(
                        '${profit >= 0 ? '+' : ''}${currencyFormat.format(profit)} (${profitPercentage.toStringAsFixed(2)}%)',
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: profit >= 0 ? AppTheme.accentGreen : Colors.redAccent,
                        ),
                      ),
                  ],
                ),
            ],
          ),
          if (subTitle != null)
            Padding(
              padding: const EdgeInsets.only(left: 24.0, top: 2.0),
              child: Text(
                subTitle,
                style: GoogleFonts.inter(
                  fontSize: 12,
                  color: AppTheme.textSecondary,
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildInvestmentItem({
    required String name,
    required String detail,
    required double amount,
    double? nav,
    double? profit,
    double? profitPercentage,
    double? sentimentScore,
    String? sentiment,
    String? status,
  }) {
    // final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);
    final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderDark),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      name,
                      style: GoogleFonts.manrope(
                        fontSize: 15,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    if (sentimentScore != null && (sentimentScore == 1 || sentimentScore == -1)) ...[
                      const SizedBox(width: 8),
                      _buildSentimentScoreIcon(sentimentScore),
                    ],
                    if (sentiment != null) ...[
                      const SizedBox(width: 8),
                      _buildSentimentBadge(sentiment),
                    ],
                    if (status != null && status != 'Active') ...[
                      const SizedBox(width: 8),
                      _buildStatusBadge(status),
                    ],
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  detail,
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    color: AppTheme.textSecondary,
                  ),
                ),
                if (profit != null && profitPercentage != null) ...[
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Text(
                        'Profit: ',
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                      Text(
                        '${profit >= 0 ? '+' : ''}${currencyFormat.format(profit)} (${profitPercentage.toStringAsFixed(2)}%)',
                        style: GoogleFonts.inter(
                          fontSize: 11,
                          fontWeight: FontWeight.w600,
                          color: profit >= 0 ? AppTheme.accentGreen : Colors.redAccent,
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                currencyFormat.format(amount),
                style: GoogleFonts.manrope(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: AppTheme.textPrimary,
                ),
              ),
              if (nav != null)
                Text(
                  'NAV: ${nav.toStringAsFixed(2)}',
                  style: GoogleFonts.inter(
                    fontSize: 11,
                    color: AppTheme.textSecondary,
                  ),
                ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSentimentScoreIcon(double score) {
    if (score == 1) {
      return const Icon(Icons.trending_up, color: AppTheme.accentGreen, size: 16);
    } else if (score == -1) {
      return const Icon(Icons.trending_down, color: Colors.redAccent, size: 16);
    }
    return const SizedBox.shrink();
  }

  Widget _buildSentimentBadge(String sentiment) {
    Color color;
    IconData icon;
    
    if (sentiment == 'HIGH' || sentiment == 'BULLISH') {
      color = AppTheme.accentGreen;
      icon = Icons.trending_up;
    } else if (sentiment == 'LOW' || sentiment == 'BEARISH') {
      color = Colors.redAccent;
      icon = Icons.trending_down;
    } else {
      color = Colors.orangeAccent;
      icon = Icons.trending_flat;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 10, color: color),
          const SizedBox(width: 2),
          Text(
            sentiment,
            style: GoogleFonts.inter(
              fontSize: 9,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(String status) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        status,
        style: GoogleFonts.inter(
          fontSize: 9,
          fontWeight: FontWeight.bold,
          color: Colors.grey,
        ),
      ),
    );
  }

  Widget _buildAssetAllocation() {
    // final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);

    // not show symbol
    final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);
    
    final data = _portfolioData!;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: AppTheme.borderDark),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: [
              SizedBox(
                height: 140,
                width: 140,
                child: PieChart(
                  PieChartData(
                    sectionsSpace: 0,
                    centerSpaceRadius: 40,
                    startDegreeOffset: -90,
                    sections: [
                      if (data.totalMfAmount > 0)
                        PieChartSectionData(
                          color: AppTheme.primaryEmerald,
                          value: data.totalMfAmount,
                          title: '',
                          radius: 25,
                        ),
                      if (data.totalPfAmount > 0)
                        PieChartSectionData(
                          color: AppTheme.accentGreen,
                          value: data.totalPfAmount,
                          title: '',
                          radius: 20,
                        ),
                      if (data.totalBondAmount > 0)
                        PieChartSectionData(
                          color: const Color(0xFF1E3A8A), // Sapphire Blue
                          value: data.totalBondAmount,
                          title: '',
                          radius: 15,
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildAllocationLegend('Mutual Funds', data.mfPercentage, AppTheme.primaryEmerald),
                    const SizedBox(height: 12),
                    _buildAllocationLegend('Private Funds', data.pfPercentage, AppTheme.accentGreen),
                    const SizedBox(height: 12),
                    _buildAllocationLegend('Bonds', data.bondPercentage, const Color(0xFF1E3A8A)),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 32),
          const Divider(height: 1, color: AppTheme.borderDark),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              _buildSummaryItem('Total Invested', currencyFormat.format(data.totalInvested)),
              _buildSummaryItem(
                'Total Profit',
                currencyFormat.format(data.totalProfit),
                valueColor: data.totalProfit >= 0 ? AppTheme.accentGreen : Colors.redAccent,
                trailing: '(${data.profitPercentage.toStringAsFixed(2)}%)',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAllocationLegend(String title, double percentage, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
            const SizedBox(width: 8),
            Text(
              title,
              style: GoogleFonts.inter(
                fontSize: 12,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
        ),
        Padding(
          padding: const EdgeInsets.only(left: 16.0),
          child: Text(
            '${percentage.toStringAsFixed(1)}%',
            style: GoogleFonts.manrope(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimary,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSummaryItem(String label, String value, {Color? valueColor, String? trailing}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: GoogleFonts.inter(
            fontSize: 12,
            color: AppTheme.textSecondary,
          ),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            Text(
              value,
              style: GoogleFonts.manrope(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: valueColor ?? AppTheme.textPrimary,
              ),
            ),
            if (trailing != null) ...[
              const SizedBox(width: 4),
              Text(
                trailing,
                style: GoogleFonts.inter(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: valueColor ?? AppTheme.textPrimary,
                ),
              ),
            ],
          ],
        ),
      ],
    );
  }
}
