import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/portfolio.dart';
import 'auth_service.dart';

class PortfolioService {
  static const String baseUrl = 'http://localhost:8080/api/v1';

  Future<PortfolioData?> getPortfolioInfo() async {
    try {
      final token = AuthService.accessToken;
      final response = await http.get(
        Uri.parse('$baseUrl/invesInfo'),
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return PortfolioData.fromJson(jsonDecode(response.body));
      }
      return null;
    } catch (e) {
      print('PortfolioService Error: $e');
      return null;
    }
  }
}
