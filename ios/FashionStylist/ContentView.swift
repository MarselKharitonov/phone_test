import SwiftUI
import PhotosUI
import UIKit

struct ContentView: View {
    @AppStorage("serverURL") private var serverURL = ""
    @State private var apiKey = ""
    @State private var keyMessage = ""
    @State private var personItem: PhotosPickerItem?
    @State private var garmentItem: PhotosPickerItem?
    @State private var personData: Data?
    @State private var garmentData: Data?
    @State private var frame = "По пояс"
    @State private var fit = "Regular"
    @State private var style = "Casual"
    @State private var note = ""
    @State private var showCamera = false
    @State private var cameraMessage = ""
    @State private var category = "tops"
    @State private var season = "Весна"
    @State private var location = ""
    @State private var budget = ""
    @State private var height = ""
    @State private var chest = ""
    @State private var waist = ""
    @State private var hips = ""
    @State private var consent = false
    @State private var serverToken = ""
    @State private var serverMessage = ""
    @State private var sending = false

    var body: some View {
        TabView {
            NavigationStack {
                Form {
                    Section("Фотографии") {
                        photoPicker("Фото человека", selection: $personItem, data: personData)
                        Button {
                            if UIImagePickerController.isSourceTypeAvailable(.camera) {
                                showCamera = true
                            } else {
                                cameraMessage = "Камера недоступна на этом устройстве."
                            }
                        } label: {
                            Label("Сделать фото", systemImage: "camera")
                        }
                        if !cameraMessage.isEmpty {
                            Text(cameraMessage).font(.caption).foregroundStyle(.secondary)
                        }
                        photoPicker("Фото одежды", selection: $garmentItem, data: garmentData)
                        Text("Фото передаются на указанный сервер только после вашего подтверждения.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Section("Образ") {
                        Picker("Кадр", selection: $frame) {
                            Text("По плечи").tag("По плечи")
                            Text("По пояс").tag("По пояс")
                            Text("Полный рост").tag("Полный рост")
                        }
                        Picker("Стиль", selection: $style) {
                            ForEach(["Casual", "Smart casual", "Business", "Streetwear"], id: \.self) { Text($0) }
                        }
                        Picker("Категория вещи", selection: $category) {
                            Text("Верх").tag("tops")
                            if frame == "Полный рост" {
                                Text("Низ").tag("bottoms")
                                Text("Платье / комбинезон").tag("one-pieces")
                            }
                        }
                        Picker("Сезон", selection: $season) {
                            ForEach(["Весна", "Лето", "Осень", "Зима"], id: \.self) { Text($0) }
                        }
                        TextField("Страна / город", text: $location)
                        TextField("Бюджет", text: $budget).keyboardType(.decimalPad)
                        Picker("Посадка", selection: $fit) {
                            ForEach(["Regular", "Slim", "Loose", "Oversized"], id: \.self) { Text($0) }
                        }
                        TextField("Пожелания", text: $note, axis: .vertical)
                    }
                    Section("Мерки, см") {
                        TextField("Рост", text: $height).keyboardType(.decimalPad)
                        TextField("Грудь", text: $chest).keyboardType(.decimalPad)
                        TextField("Талия", text: $waist).keyboardType(.decimalPad)
                        TextField("Бёдра", text: $hips).keyboardType(.decimalPad)
                        Text("Размер подбирается только по подтверждённой сетке товара.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Section {
                        Toggle("Согласен на обработку и передачу фото после подключения сервера", isOn: $consent)
                        Button("Отправить тестовую задачу") {
                            guard let person = personData, let garment = garmentData else { return }
                            let frameCode = frame == "По плечи" ? "shoulders" : (frame == "По пояс" ? "waist" : "full")
                            sending = true
                            Task {
                                do {
                                    serverMessage = try await ServerClient.submit(url: serverURL, token: serverToken,
                                        person: person, garment: garment, frame: frameCode,
                                        category: category, consent: consent)
                                } catch { serverMessage = error.localizedDescription }
                                sending = false
                            }
                        }.disabled(!consent || personData == nil || garmentData == nil || serverToken.isEmpty || sending)
                        Text(serverMessage)
                        Text("Тест соединения: генерация через Kaggle пока не подключена.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                }
                .navigationTitle("Fashion Stylist")
                .sheet(isPresented: $showCamera) {
                    CameraPicker { data in
                        personItem = nil
                        personData = data
                    }
                }
                .onChange(of: personItem) { item in
                    guard let item else { return }
                    Task { personData = try? await item.loadTransferable(type: Data.self) }
                }
                .onChange(of: frame) { value in
                    if value != "Полный рост" { category = "tops" }
                }
                .onChange(of: garmentItem) { item in
                    Task { garmentData = try? await item?.loadTransferable(type: Data.self) }
                }
            }
            .tabItem { Label("Примерка", systemImage: "person.crop.rectangle") }
            NavigationStack {
                Form {
                    Section("Домашний сервер") {
                        TextField("https://адрес:порт", text: $serverURL)
                            .textInputAutocapitalization(.never).autocorrectionDisabled()
                            .keyboardType(.URL)
                        SecureField("Токен сервера (до закрытия приложения)", text: $serverToken)
                            .textInputAutocapitalization(.never).autocorrectionDisabled()
                        Text("Требуется HTTPS с доверенным сертификатом. Не открывайте сервер напрямую в интернет.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                    Section("OpenAI API") {
                        SecureField("API-ключ", text: $apiKey)
                            .textInputAutocapitalization(.never).autocorrectionDisabled()
                        Button("Сохранить ключ") {
                            keyMessage = KeychainStore.save(apiKey) ? "Сохранено на устройстве." : "Не удалось сохранить ключ."
                        }
                        Button("Удалить ключ", role: .destructive) {
                            if KeychainStore.save("") { apiKey = ""; keyMessage = "Ключ удалён." }
                            else { keyMessage = "Не удалось удалить ключ." }
                        }
                        Text(keyMessage).font(.caption)
                        Text("Хранится в Keychain. API ещё не подключён; Plus не включает оплату API.")
                            .font(.caption).foregroundStyle(.secondary)
                    }
                }
                .navigationTitle("Настройки")
                .onAppear { apiKey = KeychainStore.read() }
            }
            .tabItem { Label("Настройки", systemImage: "gearshape") }
        }
    }

    private func photoPicker(_ title: String, selection: Binding<PhotosPickerItem?>, data: Data?) -> some View {
        PhotosPicker(selection: selection, matching: .images) {
            HStack {
                Text(title)
                Spacer()
                if let data, let image = UIImage(data: data) {
                    Image(uiImage: image).resizable().scaledToFill()
                        .frame(width: 58, height: 58).clipped().cornerRadius(6)
                } else {
                    Image(systemName: "plus.circle")
                }
            }
        }
    }
}
