using System;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        // Dictionary to store extension and its description
        Dictionary<string, string> fileInfo = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { ".mp4",  "Video file (MPEG-4 Part 14)" },
            { ".mov",  "Apple QuickTime Movie" },
            { ".avi",  "Audio Video Interleave file" },
            { ".mkv",  "Matroska Video file" },
            { ".webm", "Web-based video file" },
            { ".mp3",  "Audio file (MPEG Layer 3)" },
            { ".wav",  "Waveform audio file" },
            { ".flac", "Free Lossless Audio Codec file" },
            { ".jpg",  "JPEG Image file" },
            { ".png",  "Portable Network Graphics Image" },
            { ".gif",  "Graphics Interchange Format Image" },
            { ".bmp",  "Bitmap Image file" },
            { ".pdf",  "Portable Document Format file" },
            { ".docx", "Microsoft Word Document" },
            { ".xlsx", "Microsoft Excel Spreadsheet" },
            { ".pptx", "Microsoft PowerPoint Presentation" },
            { ".txt",  "Plain Text file" },
            { ".zip",  "Compressed ZIP Archive" },
            { ".rar",  "Compressed WinRAR Archive" },
            { ".exe",  "Windows Executable file" },
            { ".html", "HyperText Markup Language file" },
            { ".css",  "Cascading Style Sheets file" }
        };

        Console.WriteLine("==== FILE EXTENSION INFORMATION SYSTEM ====");
        Console.WriteLine("Enter a file extension (e.g., .mp4, .pdf, .jpg)");
        Console.WriteLine("Type 'exit' to quit the program.\n");

        while (true)
        {
            Console.Write("Enter extension: ");
            string input = Console.ReadLine().Trim();

            if (input.Equals("exit", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("\nThank you for using the system!");
                break;
            }

            // Ensure extension starts with dot
            if (!input.StartsWith("."))
            {
                input = "." + input;
            }

            if (fileInfo.ContainsKey(input))
            {
                Console.WriteLine($"✔ {input} = {fileInfo[input]}\n");
            }
            else
            {
                Console.WriteLine($"⚠ '{input}' is not in the system. Please try another extension.\n");
            }
        }
    }
}
