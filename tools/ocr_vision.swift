import Foundation
import Vision

struct OCRLine: Codable {
    let text: String
    let confidence: Float
    let x: Double
    let y: Double
    let width: Double
    let height: Double
}

struct OCRResult: Codable {
    let path: String
    let lines: [OCRLine]
}

if CommandLine.arguments.count < 2 {
    fputs("usage: ocr_vision <image> [image...]\n", stderr)
    exit(2)
}

let encoder = JSONEncoder()
encoder.outputFormatting = [.withoutEscapingSlashes]

for path in CommandLine.arguments.dropFirst() {
    let url = URL(fileURLWithPath: path)
    var lines: [OCRLine] = []

    let request = VNRecognizeTextRequest { request, error in
        if let error = error {
            fputs("OCR error for \(path): \(error.localizedDescription)\n", stderr)
            return
        }

        let observations = (request.results as? [VNRecognizedTextObservation]) ?? []
        for observation in observations {
            guard let candidate = observation.topCandidates(1).first else { continue }
            let box = observation.boundingBox
            lines.append(
                OCRLine(
                    text: candidate.string,
                    confidence: candidate.confidence,
                    x: box.origin.x,
                    y: box.origin.y,
                    width: box.size.width,
                    height: box.size.height
                )
            )
        }
    }

    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["ja-JP", "zh-Hans", "en-US"]

    do {
        let handler = VNImageRequestHandler(url: url)
        try handler.perform([request])
        let result = OCRResult(path: path, lines: lines)
        let data = try encoder.encode(result)
        if let text = String(data: data, encoding: .utf8) {
            print(text)
        }
    } catch {
        fputs("OCR failed for \(path): \(error.localizedDescription)\n", stderr)
        exit(1)
    }
}
