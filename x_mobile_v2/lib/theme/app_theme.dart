import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  static const Color primaryEmerald = Color(0xFF10B981); // Vibrant Emerald
  static const Color darkEmerald = Color(0xFF064E3B);    // Deep background emerald
  static const Color surfaceDark = Color(0xFF111827);    // Charcoal Surface
  static const Color backgroundDark = Color(0xFF020617); // Deepest Background
  static const Color textPrimary = Color(0xFFF9FAFB);    // Near white text
  static const Color textSecondary = Color(0xFF9CA3AF);  // Muted gray text
  static const Color accentGreen = Color(0xFF34D399);    // Lighter accent green
  static const Color borderDark = Color(0xFF1F2937);     // Darker borders

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: const ColorScheme.dark(
        primary: primaryEmerald,
        surface: surfaceDark,
        onSurface: textPrimary,
        background: backgroundDark,
        onBackground: textPrimary,
        secondary: accentGreen,
      ),
      scaffoldBackgroundColor: backgroundDark,
      textTheme: TextTheme(
        displayLarge: GoogleFonts.manrope(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: textPrimary,
          letterSpacing: -0.5,
        ),
        displayMedium: GoogleFonts.manrope(
          fontSize: 24,
          fontWeight: FontWeight.bold,
          color: textPrimary,
        ),
        headlineMedium: GoogleFonts.manrope(
          fontSize: 20,
          fontWeight: FontWeight.w600,
          color: textPrimary,
        ),
        bodyLarge: GoogleFonts.inter(
          fontSize: 16,
          fontWeight: FontWeight.normal,
          color: textPrimary,
        ),
        bodyMedium: GoogleFonts.inter(
          fontSize: 14,
          color: textSecondary,
        ),
        labelLarge: GoogleFonts.inter(
          fontSize: 12,
          fontWeight: FontWeight.w500,
          letterSpacing: 0.5,
          color: textSecondary,
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: backgroundDark,
        elevation: 0,
        centerTitle: false,
        iconTheme: IconThemeData(color: textPrimary),
        titleTextStyle: TextStyle(
          color: textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.bold,
        ),
      ),
      cardTheme: CardThemeData(
        color: surfaceDark,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: borderDark, width: 1),
        ),
      ),
    );
  }
}
