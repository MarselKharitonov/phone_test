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
                        Text("Фотографии остаются на устройстве. Автоматическая отправка пока не подключена.")
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
                        Picker("Посадка", selection: $fit) {
                            ForEach(["Regular", "Slim", "Loose", "Oversized"], id: \.self) { Text($0) }
                        }
                        TextField("Пожелания", text: $note, axis: .vertical)
                    }
                    Section {
                        Button("Создать примерку") { }.disabled(true)
                        Text("Генерация через домашний сервер и Kaggle ещё не реализована.")
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
                        Text("Адрес пока сохраняется только как настройка. Соединение не реализовано.")
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
