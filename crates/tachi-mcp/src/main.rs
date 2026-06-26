fn main() {
    let args = std::env::args().collect::<Vec<_>>();
    if let Err(err) = tachi_mcp::stdio::run(&args) {
        eprintln!("{err}");
        std::process::exit(1);
    }
}
