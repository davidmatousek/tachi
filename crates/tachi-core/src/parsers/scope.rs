use crate::parsers::table::parse_markdown_table;

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ScopeData {
    pub components: Vec<ScopeComponent>,
    pub data_flows: Vec<DataFlow>,
    pub trust_boundaries: Vec<TrustBoundary>,
    pub boundary_crossings: Vec<BoundaryCrossing>,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct ScopeComponent {
    pub name: String,
    pub kind: String,
    pub description: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct DataFlow {
    pub source: String,
    pub destination: String,
    pub data: String,
    pub protocol: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct TrustBoundary {
    pub zone: String,
    pub trust_level: String,
    pub components: String,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct BoundaryCrossing {
    pub crossing: String,
    pub from_zone: String,
    pub to_zone: String,
    pub components: String,
    pub controls: String,
}

pub fn parse_scope_data(content: &str) -> ScopeData {
    let mut result = ScopeData::default();

    for row in parse_markdown_table(content, "### Components") {
        result.components.push(ScopeComponent {
            name: row.get("Component").cloned().unwrap_or_default(),
            kind: row.get("Type").cloned().unwrap_or_default(),
            description: row.get("Description").cloned().unwrap_or_default(),
        });
    }

    for row in parse_markdown_table(content, "### Data Flows") {
        result.data_flows.push(DataFlow {
            source: row.get("Source").cloned().unwrap_or_default(),
            destination: row.get("Destination").cloned().unwrap_or_default(),
            data: row.get("Data").cloned().unwrap_or_default(),
            protocol: row.get("Protocol").cloned().unwrap_or_default(),
        });
    }

    for row in parse_markdown_table(content, "### Trust Zones") {
        result.trust_boundaries.push(TrustBoundary {
            zone: row.get("Zone").cloned().unwrap_or_default(),
            trust_level: row.get("Trust Level").cloned().unwrap_or_default(),
            components: row.get("Components").cloned().unwrap_or_default(),
        });
    }

    for row in parse_markdown_table(content, "### Boundary Crossings") {
        result.boundary_crossings.push(BoundaryCrossing {
            crossing: row.get("Crossing").cloned().unwrap_or_default(),
            from_zone: row.get("From Zone").cloned().unwrap_or_default(),
            to_zone: row.get("To Zone").cloned().unwrap_or_default(),
            components: row.get("Components").cloned().unwrap_or_default(),
            controls: row.get("Controls").cloned().unwrap_or_default(),
        });
    }

    result
}
