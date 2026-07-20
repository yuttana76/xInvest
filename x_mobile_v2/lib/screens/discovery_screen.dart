import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

class DiscoveryScreen extends StatelessWidget {
  const DiscoveryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            backgroundColor: AppTheme.backgroundDark,
            expandedHeight: 100,
            floating: true,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(
                'Explore Funds',
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
                onPressed: () {},
                icon: const Icon(Icons.search, color: AppTheme.primaryEmerald),
              ),
              const SizedBox(width: 8),
            ],
          ),
          SliverPadding(
            padding: const EdgeInsets.all(24),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _buildSectionHeader('Recommended Funds'),
                const SizedBox(height: 16),
                _buildFundCard(context, 'Global Tech Alpha', 'Technology • High Growth', '+24.5%'),
                _buildFundCard(context, 'Sustainable Energy', 'ESG • Sector Focus', '+12.8%'),
                _buildFundCard(context, 'Prime Real Estate', 'Property • Low Risk', '+4.2%'),
                const SizedBox(height: 32),
                _buildSectionHeader('Top Gainers'),
                const SizedBox(height: 16),
                _buildFundListItem(context, 'Venture Cap IV', '+45.2%'),
                _buildFundListItem(context, 'Fintech Pro', '+31.8%'),
                _buildFundListItem(context, 'Emerging Blue', '+28.4%'),
                const SizedBox(height: 32),
                _buildSectionHeader('Low Risk'),
                const SizedBox(height: 16),
                _buildFundListItem(context, 'Sovereign Bonds', '+3.2%'),
                _buildFundListItem(context, 'Liquidity Plus', '+4.1%'),
                _buildFundListItem(context, 'Global Defensives', '+5.5%'),
                const SizedBox(height: 32),
                _buildSectionHeader('ESG Funds'),
                const SizedBox(height: 16),
                _buildFundListItem(context, 'Clean Water II', '+8.2%'),
                _buildFundListItem(context, 'Solar Harvest', '+15.4%'),
                _buildFundListItem(context, 'Ethical Alpha', '+11.2%'),
              ]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: GoogleFonts.manrope(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: AppTheme.textPrimary,
      ),
    );
  }

  Widget _buildFundCard(BuildContext context, String name, String type, String returnRate) {
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
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  name,
                  style: GoogleFonts.manrope(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.textPrimary,
                  ),
                ),
                Text(
                  returnRate,
                  style: GoogleFonts.manrope(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: AppTheme.accentGreen,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 4),
            Text(
              type,
              style: GoogleFonts.inter(
                fontSize: 13,
                color: AppTheme.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFundListItem(BuildContext context, String name, String returnRate) {
    return InkWell(
      onTap: () => Navigator.pushNamed(context, '/fund-detail', arguments: name),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: AppTheme.surfaceDark,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppTheme.borderDark),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              name,
              style: GoogleFonts.manrope(
                fontSize: 14,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
            Text(
              returnRate,
              style: GoogleFonts.inter(
                fontSize: 14,
                fontWeight: FontWeight.bold,
                color: AppTheme.accentGreen,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
