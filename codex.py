import os
import httpx
import json
from typing import Any, Optional
from typing_extensions import Annotated
from mcp.server.fastmcp import FastMCP

CONGRESS_API_BASE = "https://api.congress.gov/v3"
CONGRESS_API_KEY = os.getenv("CONGRESS_API_KEY")
if not CONGRESS_API_KEY:
    print("Error: CONGRESS_API_KEY environment variable not set.")
    raise RuntimeError("CONGRESS_API_KEY environment variable must be set to make API requests")

USER_AGENT = "codex/1.0"

mcp = FastMCP("codex")

async def make_congress_request(
    endpoint: str, params: Optional[dict[str, Any]] = None
) -> str:
    """Makes a request to the Congress.gov API and returns the JSON response as a string."""
    if not CONGRESS_API_KEY:
        return json.dumps({"error": "API key is not configured."})

    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    full_params = {"api_key": CONGRESS_API_KEY}
    if params:
        full_params.update(params)

    url = f"{CONGRESS_API_BASE}{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            print(f"Making request to: {url} with params: {params}")
            response = await client.get(
                url, headers=headers, params=full_params, timeout=30.0
            )
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as exc:
            error_detail = f"HTTP error {exc.response.status_code} while requesting {exc.request.url!r}."
            try:
                error_content = exc.response.json()
                error_detail += f" Response: {json.dumps(error_content)}"
            except json.JSONDecodeError:
                error_detail += f" Response body: {exc.response.text}"
            print(f"Error making Congress API request: {error_detail}")
            return json.dumps({"error": error_detail})
        except Exception as exc:
            error_detail = f"An unexpected error occurred: {exc}"
            print(f"Error making Congress API request: {error_detail}")
            return json.dumps({"error": error_detail})

# --- Amendment Tools ---

@mcp.tool()
async def list_amendments(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists amendments across all congresses, sorted by date of latest action."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request("/amendment", params)

@mcp.tool()
async def list_amendments_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists amendments for a specific congress, sorted by date of latest action."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request(f"/amendment/{congress}", params)

@mcp.tool()
async def list_amendments_by_type(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    amendmentType: Annotated[str, "Type: 'hamdt', 'samdt', or 'suamdt'"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists amendments for a specific congress and type, sorted by date of latest action."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request(f"/amendment/{congress}/{amendmentType}", params)

@mcp.tool()
async def get_amendment_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    amendmentType: Annotated[str, "Type: 'hamdt', 'samdt', or 'suamdt'"],
    amendmentNumber: Annotated[int, "The amendment's assigned number"],
) -> str:
    """Gets detailed information for a specific amendment."""
    return await make_congress_request(f"/amendment/{congress}/{amendmentType}/{amendmentNumber}")

@mcp.tool()
async def get_amendment_actions(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    amendmentType: Annotated[str, "Type: 'hamdt', 'samdt', or 'suamdt'"],
    amendmentNumber: Annotated[int, "The amendment's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of actions for a specific amendment."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/amendment/{congress}/{amendmentType}/{amendmentNumber}/actions", params)

@mcp.tool()
async def get_amendment_cosponsors(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    amendmentType: Annotated[str, "Type: 'hamdt', 'samdt', or 'suamdt'"],
    amendmentNumber: Annotated[int, "The amendment's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of cosponsors for a specific amendment."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/amendment/{congress}/{amendmentType}/{amendmentNumber}/cosponsors", params)

@mcp.tool()
async def get_amendments_to_amendment(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    amendmentType: Annotated[str, "Type: 'hamdt', 'samdt', or 'suamdt'"],
    amendmentNumber: Annotated[int, "The amendment's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of amendments *to* a specific amendment."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/amendment/{congress}/{amendmentType}/{amendmentNumber}/amendments", params)

@mcp.tool()
async def get_amendment_text(
    congress: Annotated[int, "Congress number (117 onwards for this endpoint)"],
    amendmentType: Annotated[str, "Type: 'hamdt' or 'samdt'"],
    amendmentNumber: Annotated[int, "The amendment's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of text versions for a specific amendment (117th Congress onwards)."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/amendment/{congress}/{amendmentType}/{amendmentNumber}/text", params)

# --- Bill Tools ---

@mcp.tool()
async def list_bills(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    sort: Annotated[Optional[str], "Sort order ('updateDate+asc' or 'updateDate+desc')"] = None,
) -> str:
    """Lists bills across all congresses, sorted by date of latest action by default."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if sort:
        params["sort"] = sort
    return await make_congress_request("/bill", params)

@mcp.tool()
async def list_bills_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    sort: Annotated[Optional[str], "Sort order ('updateDate+asc' or 'updateDate+desc')"] = None,
) -> str:
    """Lists bills for a specific congress, sorted by date of latest action by default."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if sort:
        params["sort"] = sort
    return await make_congress_request(f"/bill/{congress}", params)

@mcp.tool()
async def list_bills_by_type(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    sort: Annotated[Optional[str], "Sort order ('updateDate+asc' or 'updateDate+desc')"] = None,
) -> str:
    """Lists bills for a specific congress and bill type."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if sort:
        params["sort"] = sort
    return await make_congress_request(f"/bill/{congress}/{billType}", params)

@mcp.tool()
async def get_bill_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
) -> str:
    """Gets detailed information for a specific bill."""
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}")

@mcp.tool()
async def get_bill_actions(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of actions for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/actions", params)

@mcp.tool()
async def get_bill_amendments(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of amendments for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/amendments", params)

@mcp.tool()
async def get_bill_committees(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of committees for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/committees", params)

@mcp.tool()
async def get_bill_cosponsors(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of cosponsors for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/cosponsors", params)

@mcp.tool()
async def get_bill_related_bills(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of related bills for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/relatedbills", params)

@mcp.tool()
async def get_bill_subjects(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of subjects for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/subjects", params)

@mcp.tool()
async def get_bill_summaries(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of summaries for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/summaries", params)

@mcp.tool()
async def get_bill_text(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of text versions for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/text", params)

@mcp.tool()
async def get_bill_titles(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    billNumber: Annotated[int, "The bill's assigned number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of titles for a specific bill."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bill/{congress}/{billType}/{billNumber}/titles", params)

# --- Committee Tools ---

@mcp.tool()
async def list_committees(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    chamber: Annotated[Optional[str], "Chamber: 'house', 'senate', or 'joint'"] = None,
) -> str:
    """Lists committees across all congresses."""
    params = {"limit": limit, "offset": offset}
    if chamber:
        params["chamber"] = chamber
    return await make_congress_request("/committee", params)

@mcp.tool()
async def list_committees_by_chamber(
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists committees for a specific chamber."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/committee/{chamber}", params)

@mcp.tool()
async def get_committee_details(
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    committeeCode: Annotated[str, "The committee code"],
) -> str:
    """Gets detailed information for a specific committee."""
    return await make_congress_request(f"/committee/{chamber}/{committeeCode}")

@mcp.tool()
async def get_committee_bills(
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    committeeCode: Annotated[str, "The committee code"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of bills for a specific committee."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/committee/{chamber}/{committeeCode}/bills", params)

@mcp.tool()
async def get_committee_members(
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    committeeCode: Annotated[str, "The committee code"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of members for a specific committee."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/committee/{chamber}/{committeeCode}/members", params)

# --- Committee Report Tools ---

@mcp.tool()
async def list_committee_reports(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee reports across all congresses."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request("/committee-report", params)

@mcp.tool()
async def list_committee_reports_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    conference: Annotated[Optional[bool], "Filter to include only conference reports"] = None,
) -> str:
    """Lists committee reports for a specific congress."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if conference is not None:
        params["conference"] = str(conference).lower()
    return await make_congress_request(f"/committee-report/{congress}", params)

@mcp.tool()
async def list_committee_reports_by_type(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    reportType: Annotated[str, "The report type code"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee reports for a specific congress and report type."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request(f"/committee-report/{congress}/{reportType}", params)

@mcp.tool()
async def get_committee_report_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    reportType: Annotated[str, "The report type code"],
    reportNumber: Annotated[int, "The report number"],
) -> str:
    """Gets detailed information for a specific committee report."""
    return await make_congress_request(f"/committee-report/{congress}/{reportType}/{reportNumber}")

# --- Committee Print Tools ---

@mcp.tool()
async def list_committee_prints(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee prints across all congresses."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request("/committee-print", params)

@mcp.tool()
async def list_committee_prints_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee prints for a specific congress."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request(f"/committee-print/{congress}", params)

@mcp.tool()
async def list_committee_prints_by_chamber(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee prints for a specific congress and chamber."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request(f"/committee-print/{congress}/{chamber}", params)

@mcp.tool()
async def get_committee_print_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    jacketNumber: Annotated[str, "The jacket number"],
) -> str:
    """Gets detailed information for a specific committee print."""
    return await make_congress_request(f"/committee-print/{congress}/{chamber}/{jacketNumber}")

# --- Committee Meeting Tools ---

@mcp.tool()
async def list_committee_meetings(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee meetings across all congresses."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request("/committee-meeting", params)

@mcp.tool()
async def list_committee_meetings_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee meetings for a specific congress."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request(f"/committee-meeting/{congress}", params)

@mcp.tool()
async def list_committee_meetings_by_chamber(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
) -> str:
    """Lists committee meetings for a specific congress and chamber."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    return await make_congress_request(f"/committee-meeting/{congress}/{chamber}", params)

@mcp.tool()
async def get_committee_meeting_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    eventId: Annotated[str, "The event ID"],
) -> str:
    """Gets detailed information for a specific committee meeting."""
    return await make_congress_request(f"/committee-meeting/{congress}/{chamber}/{eventId}")

# --- Member Tools ---

@mcp.tool()
async def list_members(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    currentMember: Annotated[Optional[bool], "Filter to only current members"] = None,
) -> str:
    """Lists members across all congresses."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if currentMember is not None:
        params["currentMember"] = str(currentMember).lower()
    return await make_congress_request("/member", params)

@mcp.tool()
async def get_member_details(
    bioguideId: Annotated[str, "The member's bioguide ID"],
) -> str:
    """Gets detailed information for a specific member."""
    return await make_congress_request(f"/member/{bioguideId}")

@mcp.tool()
async def get_member_sponsored_legislation(
    bioguideId: Annotated[str, "The member's bioguide ID"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of sponsored legislation for a specific member."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/member/{bioguideId}/sponsored-legislation", params)

@mcp.tool()
async def get_member_cosponsored_legislation(
    bioguideId: Annotated[str, "The member's bioguide ID"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of cosponsored legislation for a specific member."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/member/{bioguideId}/cosponsored-legislation", params)

@mcp.tool()
async def list_members_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists members for a specific congress."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/member/congress/{congress}", params)

# --- Nomination Tools ---

@mcp.tool()
async def list_nominations(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists nominations across all congresses."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/nomination", params)

@mcp.tool()
async def list_nominations_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists nominations for a specific congress."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/nomination/{congress}", params)

@mcp.tool()
async def get_nomination_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    nominationNumber: Annotated[int, "The nomination number"],
) -> str:
    """Gets detailed information for a specific nomination."""
    return await make_congress_request(f"/nomination/{congress}/{nominationNumber}")

@mcp.tool()
async def get_nomination_actions(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    nominationNumber: Annotated[int, "The nomination number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of actions for a specific nomination."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/nomination/{congress}/{nominationNumber}/actions", params)

# --- Treaty Tools ---

@mcp.tool()
async def list_treaties(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists treaties across all congresses."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/treaty", params)

@mcp.tool()
async def list_treaties_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists treaties for a specific congress."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/treaty/{congress}", params)

@mcp.tool()
async def get_treaty_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    treatyNumber: Annotated[int, "The treaty number"],
) -> str:
    """Gets detailed information for a specific treaty."""
    return await make_congress_request(f"/treaty/{congress}/{treatyNumber}")

@mcp.tool()
async def get_treaty_actions(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    treatyNumber: Annotated[int, "The treaty number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of actions for a specific treaty."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/treaty/{congress}/{treatyNumber}/actions", params)

# --- Congressional Record Tools ---

@mcp.tool()
async def list_congressional_records(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Congressional Record entries."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/congressional-record", params)

@mcp.tool()
async def list_daily_congressional_records(
    volumeNumber: Annotated[int, "The volume number"],
    issueNumber: Annotated[int, "The issue number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Daily Congressional Record articles for a specific volume and issue."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/daily-congressional-record/{volumeNumber}/{issueNumber}/articles", params)

@mcp.tool()
async def list_bound_congressional_records(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Bound Congressional Record entries."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/bound-congressional-record", params)

@mcp.tool()
async def list_bound_congressional_records_by_year(
    year: Annotated[str, "The year (YYYY)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Bound Congressional Record entries for a specific year."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bound-congressional-record/{year}", params)

@mcp.tool()
async def list_bound_congressional_records_by_month(
    year: Annotated[str, "The year (YYYY)"],
    month: Annotated[str, "The month (MM)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Bound Congressional Record entries for a specific year and month."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bound-congressional-record/{year}/{month}", params)

@mcp.tool()
async def list_bound_congressional_records_by_day(
    year: Annotated[str, "The year (YYYY)"],
    month: Annotated[str, "The month (MM)"],
    day: Annotated[str, "The day (DD)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Bound Congressional Record entries for a specific date."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/bound-congressional-record/{year}/{month}/{day}", params)

# --- Congress Tools ---

@mcp.tool()
async def list_congresses(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists information about congresses."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/congress", params)

@mcp.tool()
async def get_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"]
) -> str:
    """Gets information about a specific congress."""
    return await make_congress_request(f"/congress/{congress}")

@mcp.tool()
async def get_current_congress() -> str:
    """Gets information about the current congress."""
    return await make_congress_request("/congress/current")

# --- Summaries Tools ---

@mcp.tool()
async def list_summaries(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    sort: Annotated[Optional[str], "Sort order ('updateDate+asc' or 'updateDate+desc')"] = None,
) -> str:
    """Lists bill summaries across all congresses, sorted by date of latest update."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if sort:
        params["sort"] = sort
    return await make_congress_request("/summaries", params)

@mcp.tool()
async def list_summaries_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    sort: Annotated[Optional[str], "Sort order ('updateDate+asc' or 'updateDate+desc')"] = None,
) -> str:
    """Lists bill summaries for a specific congress, sorted by date of latest update."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if sort:
        params["sort"] = sort
    return await make_congress_request(f"/summaries/{congress}", params)

@mcp.tool()
async def list_summaries_by_bill_type(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    billType: Annotated[str, "Type: 'hr', 's', 'hjres', 'sjres', etc."],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    fromDateTime: Annotated[Optional[str], "Start date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    toDateTime: Annotated[Optional[str], "End date filter (YYYY-MM-DDTHH:mm:ssZ)"] = None,
    sort: Annotated[Optional[str], "Sort order ('updateDate+asc' or 'updateDate+desc')"] = None,
) -> str:
    """Lists bill summaries for a specific congress and bill type."""
    params = {"limit": limit, "offset": offset}
    if fromDateTime:
        params["fromDateTime"] = fromDateTime
    if toDateTime:
        params["toDateTime"] = toDateTime
    if sort:
        params["sort"] = sort
    return await make_congress_request(f"/summaries/{congress}/{billType}", params)

# --- Hearing Tools ---

@mcp.tool()
async def list_hearings(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists hearings across all congresses."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/hearing", params)

@mcp.tool()
async def list_hearings_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
    chamber: Annotated[Optional[str], "Chamber: 'house', 'senate', or 'joint'"] = None,
    committee: Annotated[Optional[str], "Committee code"] = None,
) -> str:
    """Lists hearings for a specific congress."""
    params = {"limit": limit, "offset": offset}
    if chamber:
        params["chamber"] = chamber
    if committee:
        params["committee"] = committee
    return await make_congress_request(f"/hearing/{congress}", params)

@mcp.tool()
async def get_hearing_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    chamber: Annotated[str, "Chamber: 'house', 'senate', or 'joint'"],
    jacketNumber: Annotated[str, "The hearing jacket number"],
) -> str:
    """Gets detailed information for a specific hearing."""
    return await make_congress_request(f"/hearing/{congress}/{chamber}/{jacketNumber}")

# --- Communication Tools ---

@mcp.tool()
async def list_house_communications(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists House communications across all congresses."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/house-communication", params)

@mcp.tool()
async def list_house_communications_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists House communications for a specific congress."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/house-communication/{congress}", params)

@mcp.tool()
async def get_house_communication_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    communicationType: Annotated[str, "The communication type code"],
    communicationNumber: Annotated[int, "The communication number"],
) -> str:
    """Gets detailed information for a specific House communication."""
    return await make_congress_request(f"/house-communication/{congress}/{communicationType}/{communicationNumber}")

@mcp.tool()
async def list_senate_communications(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Senate communications across all congresses."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/senate-communication", params)

@mcp.tool()
async def get_senate_communication_details(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    communicationType: Annotated[str, "The communication type code"],
    communicationNumber: Annotated[int, "The communication number"],
) -> str:
    """Gets detailed information for a specific Senate communication."""
    return await make_congress_request(f"/senate-communication/{congress}/{communicationType}/{communicationNumber}")

@mcp.tool()
async def list_senate_communications_by_congress(
    congress: Annotated[int, "The congress number (e.g., 117)"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Senate communications for a specific congress."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/senate-communication/{congress}", params)

# --- House Requirement Tools ---

@mcp.tool()
async def list_house_requirements(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists House requirements."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/house-requirement", params)

@mcp.tool()
async def get_house_requirement_details(
    requirementNumber: Annotated[int, "The requirement number"],
) -> str:
    """Gets detailed information for a specific House requirement."""
    return await make_congress_request(f"/house-requirement/{requirementNumber}")

@mcp.tool()
async def get_house_requirement_matching_communications(
    requirementNumber: Annotated[int, "The requirement number"],
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Gets the list of matching communications for a specific House requirement."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request(f"/house-requirement/{requirementNumber}/matching-communications", params)

# --- CRS Report Tools ---

@mcp.tool()
async def list_crs_reports(
    limit: Annotated[Optional[int], "Number of records (max 250)"] = 100,
    offset: Annotated[Optional[int], "Starting record index (0-based)"] = 0,
) -> str:
    """Lists Congressional Research Service reports."""
    params = {"limit": limit, "offset": offset}
    return await make_congress_request("/crsreport", params)

@mcp.tool()
async def get_crs_report_details(
    reportNumber: Annotated[str, "The report number"],
) -> str:
    """Gets detailed information for a specific CRS report."""
    return await make_congress_request(f"/crsreport/{reportNumber}")

if __name__ == "__main__":
    if not CONGRESS_API_KEY:
        print("Warning: Server is running without CONGRESS_API_KEY set.")
        print("         API calls will likely fail.")
    mcp.run(transport='stdio')
