import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundDark,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            backgroundColor: AppTheme.backgroundDark,
            expandedHeight: 180,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                color: AppTheme.backgroundDark,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const SizedBox(height: 40),
                    Container(
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primaryEmerald.withOpacity(0.2),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: const CircleAvatar(
                        radius: 40,
                        backgroundColor: AppTheme.primaryEmerald,
                        child: Icon(Icons.person, color: Colors.white, size: 40),
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'Alexander Vance',
                      style: GoogleFonts.manrope(
                        fontSize: 22,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.textPrimary,
                        letterSpacing: -0.5,
                      ),
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.workspace_premium, color: AppTheme.accentGreen, size: 16),
                        const SizedBox(width: 4),
                        Text(
                          'Private Client • Verified Status',
                          style: GoogleFonts.inter(
                            fontSize: 12,
                            color: AppTheme.textSecondary,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
          SliverPadding(
            padding: const EdgeInsets.all(24),
            sliver: SliverList(
              delegate: SliverChildListDelegate([
                _buildSectionHeader('Account Settings'),
                const SizedBox(height: 16),
                _buildSettingsTile(
                  icon: Icons.shield_outlined,
                  title: 'Security',
                  subtitle: 'Biometrics, 2FA, Passkeys',
                ),
                _buildSettingsTile(
                  icon: Icons.notifications_none_outlined,
                  title: 'Notifications',
                  subtitle: 'Transaction alerts, Market news',
                ),
                _buildSettingsTile(
                  icon: Icons.account_balance_outlined,
                  title: 'Linked Bank Accounts',
                  subtitle: 'Manage 3 external connections',
                ),
                _buildSettingsTile(
                  icon: Icons.help_outline,
                  title: 'Help Center',
                  subtitle: 'Support tickets, FAQ, Live chat',
                ),
                const SizedBox(height: 48),
                Center(
                  child: Column(
                    children: [
                      Text(
                        'Version 2.4.1 (Emerald Series)',
                        style: GoogleFonts.inter(
                          fontSize: 12,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextButton(
                        onPressed: () => Navigator.pushReplacementNamed(context, '/login'),
                        child: Text(
                          'Sign Out',
                          style: GoogleFonts.inter(
                            color: Colors.redAccent,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 100),
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
        fontSize: 14,
        fontWeight: FontWeight.bold,
        color: AppTheme.textSecondary,
        letterSpacing: 0.5,
      ),
    );
  }

  Widget _buildSettingsTile({required IconData icon, required String title, required String subtitle}) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.borderDark),
      ),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppTheme.primaryEmerald.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, color: AppTheme.primaryEmerald, size: 20),
        ),
        title: Text(
          title,
          style: GoogleFonts.manrope(
            fontSize: 15,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimary,
          ),
        ),
        subtitle: Text(
          subtitle,
          style: GoogleFonts.inter(
            fontSize: 12,
            color: AppTheme.textSecondary,
          ),
        ),
        trailing: const Icon(Icons.chevron_right, color: AppTheme.borderDark),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        onTap: () {},
      ),
    );
  }
}
