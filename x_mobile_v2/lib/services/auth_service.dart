import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const String baseUrl = 'http://localhost:8000/api/v1/auth';
  static String? _accessToken;

  static String? get accessToken => _accessToken;

  Future<bool> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return true;
      }
      return false;
    } catch (e) {
      print('AuthService Error: $e');
      return false;
    }
  }

  Future<bool> verifyOtp(String username, String otp) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/verify-otp/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'otp_code': otp,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        _accessToken = data['access'];
        return true;
      }
      return false;
    } catch (e) {
      print('AuthService Error: $e');
      return false;
    }
  }
}
