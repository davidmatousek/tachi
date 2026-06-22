use tachi_core::facade::crate_name;

#[test]
fn parity_crate_reports_its_name() {
    assert_eq!(crate_name(), "tachi-core");
}
