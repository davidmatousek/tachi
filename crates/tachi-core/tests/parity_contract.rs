use tachi_core::parity::crate_name;

#[test]
fn parity_crate_reports_its_name() {
    assert_eq!(crate_name(), "tachi-core");
}
