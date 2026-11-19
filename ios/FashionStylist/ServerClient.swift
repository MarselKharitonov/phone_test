import Foundation

enum ServerClient {
    static func submit(url: String, token: String, person: Data, garment: Data,
                       frame: String, category: String, consent: Bool) async throws -> String {
        guard let base = URL(string: url), base.scheme?.lowercased() == "https",
              base.host != nil, base.user == nil, base.password == nil else {
            throw ClientError.invalidURL
        }
        let endpoint = base.appendingPathComponent("v1/jobs")
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.timeoutInterval = 60
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONSerialization.data(withJSONObject: [
            "person": person.base64EncodedString(), "garment": garment.base64EncodedString(),
            "frame": frame, "category": category, "consent": consent
        ])
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let response = response as? HTTPURLResponse, response.statusCode == 202,
              let object = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let state = object["state"] as? String else {
            throw ClientError.serverError
        }
        if state == "failed" { return "Сервер принял запрос, но генерация ещё не подключена." }
        return "Статус задачи: \(state)"
    }

    enum ClientError: LocalizedError {
        case invalidURL, serverError
        var errorDescription: String? {
            switch self {
            case .invalidURL: return "Укажите HTTPS-адрес сервера с доверенным сертификатом."
            case .serverError: return "Сервер отклонил запрос или вернул неизвестный ответ."
            }
        }
    }
}
