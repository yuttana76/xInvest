import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import '../theme/app_theme.dart';
import '../services/portfolio_service.dart';
import '../models/portfolio.dart';

class HomeDashboard extends StatefulWidget {
  const HomeDashboard({super.key});

  @override
  State<HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends State<HomeDashboard> {
  final PortfolioService _portfolioService = PortfolioService();
  bool _isLoading = true;
  PortfolioData? _portfolioData;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final data = await _portfolioService.getPortfolioInfo();
      if (mounted) {
        setState(() {
          _portfolioData = data;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 120,
            floating: true,
            pinned: true,
            backgroundColor: AppTheme.backgroundDark,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(
                'XInvest',
                style: GoogleFonts.manrope(
                  fontWeight: FontWeight.w800,
                  color: AppTheme.textPrimary,
                  letterSpacing: -1,
                ),
              ),
              titlePadding: const EdgeInsets.only(left: 24, bottom: 16),
            ),
            actions: [
              IconButton(
                onPressed: _loadData,
                icon: const Icon(Icons.refresh, color: AppTheme.primaryEmerald),
              ),
              IconButton(
                onPressed: () {},
                icon: const Icon(Icons.notifications_none_outlined, color: AppTheme.primaryEmerald),
              ),
              const SizedBox(width: 8),
            ],
          ),
          SliverPadding(
            padding: const EdgeInsets.all(24),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _buildPortfolioCard(context),
                if (_portfolioData != null) ...[
                  const SizedBox(height: 32),
                  _buildAssetAllocationSection(),
                ],
                const SizedBox(height: 32),
                _buildSectionHeader('Market Insights', onSeeAll: () {}),
                const SizedBox(height: 16),
                _buildInsightCard(
                  'Navigating the Q4 Volatility: Why Cash is No Longer King',
                  category: 'STRATEGY',
                ),
                _buildInsightCard(
                  'Emerging Green Bonds: The Future of Sustainable Yield',
                  category: 'TRENDING',
                ),
                const SizedBox(height: 32),
                _buildSectionHeader('Featured Funds'),
                const SizedBox(height: 16),
                _buildFundCard(
                  context,
                  'Emerald Sustainable Alpha',
                  category: 'Global ESG • Mid Risk',
                  returnRate: '+18.2%',
                ),
                _buildFundCard(
                  context,
                  'Precision AI Tech Core',
                  category: 'Technology • High Risk',
                  returnRate: '+34.5%',
                ),
                _buildFundCard(
                  context,
                  'Conservative Yield 2025',
                  category: 'Fixed Income • Low Risk',
                  returnRate: '+5.8%',
                ),
                const SizedBox(height: 100), // Spacing for bottom nav
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPortfolioCard(BuildContext context) {
    final currencyFormat = NumberFormat.currency(symbol: '', decimalDigits: 2);
    final totalValue = _portfolioData?.totalAmount ?? 0.0;
    final totalProfit = _portfolioData?.totalProfit ?? 0.0;
    final profitPercent = _portfolioData?.profitPercentage ?? 0.0;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: AppTheme.borderDark),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.5),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Total Portfolio Value',
                style: GoogleFonts.inter(
                  color: AppTheme.textSecondary,
                  fontSize: 14,
                  fontWeight: FontWeight.w500,
                ),
              ),
              if (_portfolioData != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryEmerald.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(100),
                  ),
                  child: Text(
                    '${totalProfit >= 0 ? '+' : ''}${currencyFormat.format(totalProfit)} (${profitPercent.toStringAsFixed(2)}%)',
                    style: GoogleFonts.inter(
                      color: totalProfit >= 0 ? AppTheme.primaryEmerald : Colors.redAccent,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            currencyFormat.format(totalValue),
            style: GoogleFonts.manrope(
              color: AppTheme.textPrimary,
              fontSize: 34,
              fontWeight: FontWeight.w800,
              letterSpacing: -1,
            ),
          ),
          const SizedBox(height: 20),
          _buildPortfolioBadge(),
        ],
      ),
    );
  }

  Widget _buildPortfolioBadge() {
    String label = 'Diversified';
    if (_portfolioData != null) {
      if (_portfolioData!.mfPercentage > 70) label = 'MF Focused';
      else if (_portfolioData!.pfPercentage > 70) label = 'PF Focused';
      else if (_portfolioData!.bondPercentage > 70) label = 'Conservative';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
      decoration: BoxDecoration(
        color: AppTheme.primaryEmerald.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        label,
        style: GoogleFonts.inter(
          color: AppTheme.primaryEmerald,
          fontSize: 12,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildAssetAllocationSection() {
    final data = _portfolioData!;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildSectionHeader('Asset Allocation'),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: AppTheme.surfaceDark,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: AppTheme.borderDark),
          ),
          child: Row(
            children: [
              SizedBox(
                height: 100,
                width: 100,
                child: PieChart(
                  PieChartData(
                    sectionsSpace: 0,
                    centerSpaceRadius: 30,
                    sections: [
                      if (data.totalMfAmount > 0)
                        PieChartSectionData(
                          color: AppTheme.primaryEmerald,
                          value: data.totalMfAmount,
                          title: '',
                          radius: 15,
                        ),
                      if (data.totalPfAmount > 0)
                        PieChartSectionData(
                          color: AppTheme.accentGreen,
                          value: data.totalPfAmount,
                          title: '',
                          radius: 12,
                        ),
                      if (data.totalBondAmount > 0)
                        PieChartSectionData(
                          color: const Color(0xFF1E3A8A),
                          value: data.totalBondAmount,
                          title: '',
                          radius: 10,
                        ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 24),
              Expanded(
                child: Column(
                  children: [
                    _buildLegendItem('Mutual Funds', '${data.mfPercentage.toStringAsFixed(1)}%', AppTheme.primaryEmerald),
                    const SizedBox(height: 8),
                    _buildLegendItem('Private Funds', '${data.pfPercentage.toStringAsFixed(1)}%', AppTheme.accentGreen),
                    const SizedBox(height: 8),
                    _buildLegendItem('Bonds', '${data.bondPercentage.toStringAsFixed(1)}%', const Color(0xFF1E3A8A)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildLegendItem(String label, String value, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
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
              label,
              style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textSecondary),
            ),
          ],
        ),
        Text(
          value,
          style: GoogleFonts.manrope(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textPrimary),
        ),
      ],
    );
  }

  Widget _buildSectionHeader(String title, {VoidCallback? onSeeAll}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title,
          style: GoogleFonts.manrope(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ),
        if (onSeeAll != null)
          TextButton(
            onPressed: onSeeAll,
            child: Text(
              'View All',
              style: GoogleFonts.inter(
                color: AppTheme.primaryEmerald,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildInsightCard(String title, {required String category}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderDark),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            category,
            style: GoogleFonts.inter(
              fontSize: 10,
              fontWeight: FontWeight.bold,
              letterSpacing: 1,
              color: AppTheme.primaryEmerald,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            title,
            style: GoogleFonts.manrope(
              fontSize: 16,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimary,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFundCard(BuildContext context, String name, {required String category, required String returnRate}) {
    return InkWell(
      onTap: () => Navigator.pushNamed(context, '/fund-detail', arguments: name),
      child: Container(
        margin: const EdgeInsets.only(bottom: 16),
        padding: const EdgeInsets.all(20),
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
                  Text(
                    name,
                    style: GoogleFonts.manrope(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    category,
                    style: GoogleFonts.inter(
                      fontSize: 13,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  returnRate,
                  style: GoogleFonts.manrope(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.accentGreen,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '1Y RETURN',
                  style: GoogleFonts.inter(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textSecondary,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
