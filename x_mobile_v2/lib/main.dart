import 'package:flutter/material.dart';
import 'theme/app_theme.dart';
import 'screens/main_shell.dart';
import 'screens/login_screen.dart';
import 'screens/otp_screen.dart';
import 'screens/fund_detail_screen.dart';

void main() {
  runApp(const XInvestApp());
}

class XInvestApp extends StatelessWidget {
  const XInvestApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'XInvest',
      debugShowCheckedModeBanner: false,
      themeMode: ThemeMode.dark,
      darkTheme: AppTheme.darkTheme,
      initialRoute: '/login',
      onGenerateRoute: (settings) {
        if (settings.name == '/otp') {
          final username = settings.arguments as String;
          return MaterialPageRoute(
            builder: (context) => OtpScreen(username: username),
          );
        }
        if (settings.name == '/fund-detail') {
          final fundName = settings.arguments as String;
          return MaterialPageRoute(
            builder: (context) => FundDetailScreen(fundName: fundName),
          );
        }
        return null;
      },
      routes: {
        '/login': (context) => const LoginScreen(),
        '/home': (context) => const MainShell(),
      },
    );
  }
}
