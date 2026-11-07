#!/usr/bin/env swift
// macOS Vision 框架 OCR 工具
// 用法: swift run ocr.swift image.png
// 或者: swiftc ocr.swift -o ocr && ./ocr image.png
//
// 优点:
//   ✅ 系统原生，无需下载任何模型
//   ✅ 内置中文支持，准确率高
//   ✅ 速度快，每张图片 200-500ms
//   ✅ 不会因为网络问题失败
//   ✅ 不浪费 token 在中间方案，一步到位

// 使用场景:
//   - 批量识别 AI 术语卡片编号
//   - 提取截图中的文字
//   - 验证文件名是否与图片内容匹配
//
// 编译: swiftc macos_ocr.swift -o /usr/local/bin/ocr
// 使用: ocr image.png

import Vision
import Cocoa

let args = CommandLine.arguments
guard args.count > 1 else {
    print("用法: ocr <图片文件>")
    exit(1)
}
let imgPath = args[1]

guard FileManager.default.fileExists(atPath: imgPath) else {
    print("❌ 文件不存在: \(imgPath)")
    exit(1)
}

guard let img = NSImage(contentsOfFile: imgPath),
      let cgImg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("❌ 无法读取图片")
    exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en-US"]
request.usesLanguageCorrection = true

let handler = VNImageRequestHandler(cgImage: cgImg, options: [:])

do {
    try handler.perform([request])
} catch {
    print("❌ OCR 失败: \(error)")
    exit(1)
}

guard let observations = request.results else {
    print("⚠️  未识别到文字")
    exit(0)
}

for obs in observations {
    if let text = obs.topCandidates(1).first?.string {
        print(text)
    }
}