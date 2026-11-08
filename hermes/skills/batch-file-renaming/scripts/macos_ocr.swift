#!/usr/bin/env swift
// macOS Vision Framework OCR for batch file renaming
// 这是批量重命名任务的 PREFERRED 首选方案
//
// 为什么用这个而不是其他方案：
//   ✅ 无需下载任何模型（系统原生）
//   ✅ 内置中文支持，准确率极高
//   ✅ 速度快（200-500ms/张）
//   ✅ 不会因网络问题失败
//   ✅ 不需要 pip install 任何包
//   ✅ 不浪费 token 在其他无效中间方案上 (像素匹配、指纹、模板都不要试)
//
// 🚨 用户明确指示：不要乱用其他办法浪费token，直接 OCR！
//     "你一直乱用其它的办法就是在浪费token"
//
// 编译: swiftc macos_ocr.swift -o /tmp/ocr
// 使用: /tmp/ocr image.png
// 批量: for f in *.png; do /tmp/ocr "$f"; done

import Vision
import Cocoa

let args = CommandLine.arguments
guard args.count > 1 else {
    print("Usage: ocr <image_file>")
    exit(1)
}
let imgPath = args[1]

guard FileManager.default.fileExists(atPath: imgPath) else {
    exit(1)
}

guard let img = NSImage(contentsOfFile: imgPath),
      let cgImg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
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
    exit(1)
}

guard let observations = request.results else {
    exit(0)
}

for obs in observations {
    if let text = obs.topCandidates(1).first?.string {
        print(text)
    }
}