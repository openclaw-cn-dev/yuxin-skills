// macOS Vision 框架 IP 抠图脚本（系统自带 AI，零依赖）
// 用法：swift cutout.swift <输入图> <输出 PNG>
// 需求：macOS 14+
import Foundation
import Vision
import AppKit
import CoreImage

guard CommandLine.arguments.count >= 3 else {
    FileHandle.standardError.write("Usage: swift cutout.swift <input> <output>\n".data(using: .utf8)!)
    exit(1)
}
let inPath = CommandLine.arguments[1]
let outPath = CommandLine.arguments[2]

guard let nsImg = NSImage(contentsOf: URL(fileURLWithPath: inPath)),
      let cgImg = nsImg.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("cannot load image\n".data(using: .utf8)!)
    exit(2)
}

let handler = VNImageRequestHandler(cgImage: cgImg, options: [:])
let req = VNGenerateForegroundInstanceMaskRequest()
do {
    try handler.perform([req])
} catch {
    FileHandle.standardError.write("vision request failed: \(error)\n".data(using: .utf8)!)
    exit(3)
}
guard let obs = req.results?.first else {
    FileHandle.standardError.write("no foreground instances detected\n".data(using: .utf8)!)
    exit(4)
}
do {
    let pixelBuffer = try obs.generateMaskedImage(ofInstances: obs.allInstances,
                                                  from: handler,
                                                  croppedToInstancesExtent: false)
    let ci = CIImage(cvPixelBuffer: pixelBuffer)
    let ctx = CIContext()
    guard let outCG = ctx.createCGImage(ci, from: ci.extent) else {
        FileHandle.standardError.write("CIContext render failed\n".data(using: .utf8)!)
        exit(5)
    }
    let bitmap = NSBitmapImageRep(cgImage: outCG)
    guard let png = bitmap.representation(using: .png, properties: [:]) else {
        FileHandle.standardError.write("png encode failed\n".data(using: .utf8)!)
        exit(6)
    }
    try png.write(to: URL(fileURLWithPath: outPath))
    print("OK -> \(outPath)")
} catch {
    FileHandle.standardError.write("masked image gen failed: \(error)\n".data(using: .utf8)!)
    exit(7)
}
