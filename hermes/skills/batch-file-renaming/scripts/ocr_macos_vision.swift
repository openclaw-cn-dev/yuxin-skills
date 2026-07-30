import Vision
import AppKit

// macOS Vision Framework OCR Script
// Usage: xcrun swift ocr_macos_vision.swift /path/to/image.png
//
// Designed for knowledge cards with title at the top (first ~15%)
// Crops to top region to avoid noisy content in the body

if CommandLine.arguments.count < 2 {
    print("Usage: xcrun swift ocr_macos_vision.swift <image_path>")
    exit(1)
}

let imagePath = CommandLine.arguments[1]

guard let img = NSImage(contentsOfFile: imagePath) else {
    print("ERROR: Cannot load image: \(imagePath)")
    exit(1)
}

// Crop to TOP 15% where title lives
// This avoids distracting content in the card body
let cropHeight = img.size.height * 0.15
let cropY = img.size.height - cropHeight  // Flip Y for NSImage (origin at bottom)

let cropRect = NSRect(
    x: 0,
    y: cropY,
    width: img.size.width,
    height: cropHeight
)

// Create image from cropped rect
guard let cgImage = img.cgImage(
    forProposedRect: nil,
    context: nil,
    hints: nil
) else {
    print("ERROR: Cannot create CGImage")
    exit(1)
}

// Crop in CGImage coordinates (origin at top-left)
let cgCropRect = CGRect(
    x: 0,
    y: 0,  // Top region in CG coordinates
    width: CGFloat(cgImage.width),
    height: CGFloat(cgImage.height) * 0.15
)

guard let croppedCGImage = cgImage.cropping(to: cgCropRect) else {
    print("ERROR: Cannot crop image")
    exit(1)
}

// Vision request
let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.usesLanguageCorrection = false  // Keep off for numbers/tech terms
request.recognitionLanguages = ["zh-Hans", "en-US"]

do {
    let handler = VNImageRequestHandler(
        cgImage: croppedCGImage,
        options: [:]
    )
    try handler.perform([request])
    
    guard let results = request.results else {
        print("NO_RESULTS")
        exit(0)
    }
    
    for result in results {
        if let candidate = result.topCandidates(1).first {
            print(candidate.string)
        }
    }
    
} catch {
    print("ERROR: Vision failed: \(error)")
    exit(1)
}
