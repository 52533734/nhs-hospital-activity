def test_home_page_loads(client):
    """Homepage should load successfully."""
    response = client.get("/")

    assert response.status_code == 200
    assert b"NHS Hospital Activity Explorer" in response.data


def test_providers_page_loads(client):
    """Providers page should list seeded providers."""
    response = client.get("/providers")

    assert response.status_code == 200
    assert b"NHS Providers" in response.data
    assert b"Alpha NHS Trust" in response.data


def test_providers_search_filter_returns_matching_provider(client):
    """Provider search should return matching providers."""
    response = client.get("/providers?search=Alpha")

    assert response.status_code == 200
    assert b"Alpha NHS Trust" in response.data
    assert b"Beta NHS Trust" not in response.data


def test_providers_search_filter_empty_state(client):
    """Search with no results should show empty state."""
    response = client.get("/providers?search=NoSuchProvider")

    assert response.status_code == 200
    assert b"No providers found" in response.data


def test_providers_min_admissions_filter(client):
    """Minimum admissions filter should remove low-activity providers."""
    response = client.get("/providers?min_admissions=700")

    assert response.status_code == 200
    assert b"Beta NHS Trust" in response.data
    assert b"Gamma NHS Trust" not in response.data


def test_provider_detail_page_loads(client):
    """Provider detail page should display summary sections."""
    response = client.get("/providers/1")

    assert response.status_code == 200
    assert b"Alpha NHS Trust" in response.data
    assert b"Provider Summary" in response.data
    assert b"Benchmark Comparison" in response.data


def test_provider_detail_invalid_id_returns_404(client):
    """Invalid provider ID should show the custom 404 page."""
    response = client.get("/providers/99999")

    assert response.status_code == 404
    assert b"404 - Page Not Found" in response.data


def test_compare_page_empty_state(client):
    """Compare page should ask user to select providers."""
    response = client.get("/compare")

    assert response.status_code == 200
    assert b"Please select two or three providers to compare" in response.data


def test_compare_page_rejects_duplicate_providers(client):
    """Duplicate provider selections should show an error."""
    response = client.get("/compare?provider1=1&provider2=1")

    assert response.status_code == 200
    assert b"Please select different providers for comparison" in response.data


def test_compare_page_requires_at_least_two_providers(client):
    """Selecting only one provider should show validation error."""
    response = client.get("/compare?provider1=1")

    assert response.status_code == 200
    assert b"Please select at least two providers to compare" in response.data


def test_compare_page_valid_selection(client):
    """Valid comparison should show selected provider metrics."""
    response = client.get("/compare?provider1=1&provider2=2")

    assert response.status_code == 200
    assert b"Alpha NHS Trust" in response.data
    assert b"Beta NHS Trust" in response.data
    assert b"Emergency Admissions" in response.data


def test_analytics_page_loads(client):
    """Analytics page should render provider and specialty analytics."""
    response = client.get("/analytics")

    assert response.status_code == 200
    assert b"Analytics Dashboard" in response.data
    assert b"Best Performing Providers" in response.data
    assert b"Treatment Specialty" in response.data


def test_age_analytics_page_loads(client):
    """Age analytics page should render cleaned age-band labels."""
    response = client.get("/age-analytics")

    assert response.status_code == 200
    assert b"Age-Based Analytics" in response.data
    assert b"0 - 4" in response.data
    assert b"01. 0 - 4" not in response.data


def test_unknown_page_uses_custom_404_handler(client):
    """Unknown URLs should return the custom 404 page."""
    response = client.get("/this-page-does-not-exist")

    assert response.status_code == 404
    assert b"The page you are looking for does not exist" in response.data