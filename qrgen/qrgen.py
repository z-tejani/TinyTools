import argparse
import sys

def generate_qr(data, output_file):
    try:
        import qrcode
    except ImportError:
        print("Error: 'qrcode' library is required.")
        print("pip install qrcode[pil]")
        sys.exit(1)

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(output_file)
    print(f"QR Code saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate a QR code image.")
    parser.add_argument("data", help="Text or URL to encode")
    parser.add_argument("--output", default="qrcode.png", help="Output filename (default: qrcode.png)")
    
    args = parser.parse_args()
    generate_qr(args.data, args.output)

if __name__ == "__main__":
    main()
