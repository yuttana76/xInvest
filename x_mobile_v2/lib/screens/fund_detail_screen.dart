import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../theme/app_theme.dart';

class FundDetailScreen extends StatelessWidget {
  final String fundName;
  const FundDetailScreen({super.key, required this.fundName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      appBar: AppBar(
        backgroundColor: AppTheme.surfaceDark,
        centerTitle: true,
        title: Text(
          'Fund Details',
          style: GoogleFonts.manrope(
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
            fontSize: 16,
          ),
        ),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeaderSection(),
            _buildMainMetrics(),
            _buildPerformanceChart(),
            _buildAllocationSection(),
            _buildHoldingsSection(),
            const SizedBox(height: 40),
            _buildActionButtons(),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildHeaderSection() {
    return Container(
      width: double.infinity,
      color: AppTheme.surfaceDark,
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    fundName,
                    style: GoogleFonts.manrope(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.trending_up, color: AppTheme.accentGreen, size: 16),
                      const SizedBox(width: 4),
                      Text(
                        'Bullish Momentum',
                        style: GoogleFonts.inter(
                          color: AppTheme.accentGreen,
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '\$142.84',
                    style: GoogleFonts.manrope(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  Text(
                    '+2.4(1.8%)',
                    style: GoogleFonts.inter(
                      color: AppTheme.accentGreen,
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMainMetrics() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppTheme.surfaceDark,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.borderDark),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildMetricItem('Expense Ratio', '0.45%'),
            _buildMetricDivider(),
            _buildMetricItem('Min. Invest', '\$10,000'),
            _buildMetricDivider(),
            _buildMetricItem('Risk', 'Med-High'),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricItem(String label, String value) {
    return Column(
      children: [
        Text(
          label,
          style: GoogleFonts.inter(fontSize: 10, color: AppTheme.textSecondary),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: GoogleFonts.manrope(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricDivider() {
    return Container(height: 30, width: 1, color: AppTheme.borderDark);
  }

  Widget _buildPerformanceChart() {
    return Container(
      height: 300,
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Performance History',
            style: GoogleFonts.manrope(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: LineChart(
              LineChartData(
                gridData: FlGridData(show: false),
                titlesData: FlTitlesData(show: false),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: [
                      const FlSpot(0, 3),
                      const FlSpot(2, 4),
                      const FlSpot(4, 3.5),
                      const FlSpot(6, 5),
                      const FlSpot(8, 4.5),
                      const FlSpot(10, 6),
                    ],
                    isCurved: true,
                    color: AppTheme.primaryEmerald,
                    barWidth: 3,
                    isStrokeCapRound: true,
                    dotData: FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppTheme.primaryEmerald.withOpacity(0.1),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAllocationSection() {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Sector Allocation',
            style: GoogleFonts.manrope(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              SizedBox(
                height: 140,
                width: 140,
                child: PieChart(
                  PieChartData(
                    sectionsSpace: 4,
                    centerSpaceRadius: 40,
                    sections: [
                      PieChartSectionData(value: 42, color: AppTheme.primaryEmerald, radius: 20, showTitle: false),
                      PieChartSectionData(value: 28, color: AppTheme.accentGreen, radius: 20, showTitle: false),
                      PieChartSectionData(value: 15, color: AppTheme.textSecondary, radius: 20, showTitle: false),
                      PieChartSectionData(value: 15, color: AppTheme.borderDark, radius: 20, showTitle: false),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 32),
              Expanded(
                child: Column(
                  children: [
                    _buildAllocationLegend('Solar Infra', '42%', AppTheme.primaryEmerald),
                    _buildAllocationLegend('Wind Energy', '28%', AppTheme.accentGreen),
                    _buildAllocationLegend('Battery Storage', '15%', AppTheme.textSecondary),
                    _buildAllocationLegend('Smart Grid', '15%', AppTheme.borderDark),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildAllocationLegend(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(width: 10, height: 10, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
              const SizedBox(width: 8),
              Text(label, style: GoogleFonts.inter(fontSize: 12, color: AppTheme.textSecondary)),
            ],
          ),
          Text(value, style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildHoldingsSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Top Holdings',
            style: GoogleFonts.manrope(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          _buildHoldingTile('Nextera Energy Inc', '7.42%'),
          _buildHoldingTile('Enphase Energy', '6.15%'),
          _buildHoldingTile('First Solar Inc', '5.28%'),
        ],
      ),
    );
  }

  Widget _buildHoldingTile(String name, String weight) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(name, style: GoogleFonts.inter(fontSize: 14, color: AppTheme.textPrimary)),
          Text(weight, style: GoogleFonts.manrope(fontSize: 14, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _buildActionButtons() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () {},
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                side: const BorderSide(color: AppTheme.primaryEmerald),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: Text(
                'Watchlist',
                style: GoogleFonts.manrope(color: AppTheme.primaryEmerald, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: AppTheme.primaryEmerald,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                elevation: 0,
              ),
              child: Text(
                'Invest Now',
                style: GoogleFonts.manrope(fontWeight: FontWeight.bold),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
