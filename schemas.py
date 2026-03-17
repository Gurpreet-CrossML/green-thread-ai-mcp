from typing import Optional

from pydantic import BaseModel


class EULabel(BaseModel):
    """
    EULabel model describing EU tyre label information for a tyre.

    Attributes:
        wet_grip (Optional[str]): Wet grip class (e.g. 'A'..'G') or other wet grip descriptor. None if not provided.
        noise_db (Optional[int]): External rolling noise level, typically expressed as an integer (e.g. 72). None if unknown.
        rolling_resistance (Optional[str]): Rolling resistance class or value (e.g. 'A'..'G' or a numeric code). None if not provided.
    """
    wet_grip: Optional[str] = None
    noise_db: Optional[int] = None
    rolling_resistance: Optional[str] = None


class Tyre(BaseModel):
    """
    Tyre model describing a tyre product and its commercial/technical attributes.

    Attributes:
        tyre_id (Optional[str]): Optional unique identifier for the tyre.
        name (Optional[str]): Optional name of the tyre.
        brand (Optional[str]): Manufacturer or brand name.
        model (Optional[str]): Model or variant name of the tyre.
        size (Optional[str]): Tyre size specification (e.g. "205/55 R16").
        load_index (Optional[int]): Numeric load carrying capacity index.
        speed_rating (Optional[str]): Speed rating letter (e.g. "H", "V").
        season (Optional[str]): Season classification (e.g. "summer", "winter", "all-season").
        eu_label (EULabel): EU label object containing efficiency/safety ratings (required).
        features (Optional[list]): List of additional features or attributes (e.g. ["run-flat", "noise-reduced"]).
        description (Optional[str]): Optional description of the tyre.
        price (Optional[float]): Unit price of the tyre.
        currency (Optional[str]): Currency code for the price (e.g. "EUR", "USD").
        availability (bool): Whether the tyre is available for purchase. Defaults to False.
        in_stock (Optional[int]): Quantity currently in stock.
        delivery_time_hrs (Optional[int]): Estimated delivery time in hours.
        buy_link (Optional[str]): URL linking to a purchase page for the tyre.
        image_url (Optional[str]): URL to an image of the tyre.
        is_premium (Optional[bool]): Filter by premium status.

    Notes:
        - This class is intended as a Pydantic BaseModel for validation and serialization.
        - Fields typed as Optional[...] may be None when information is missing.
        - eu_label is expected to be an instance of EULabel representing official EU tyre ratings.
    """
    tyre_id: Optional[str] = None
    name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    size: Optional[str] = None
    load_index: Optional[int] = None
    speed_rating: Optional[str] = None
    season: Optional[str] = None
    eu_label: EULabel
    features: Optional[list] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    availability: bool = False
    in_stock: Optional[int] = None
    delivery_time_hrs: Optional[int] = None
    buy_link: Optional[str] = None
    image_url: Optional[str] = None
    is_premium: Optional[bool] = False,

    def __init__(self, **data):
        """
        Initialize a Tyre instance with provided data.

        Parameters
        ----------
        **data : dict
            Keyword arguments corresponding to Tyre attributes.

        Returns
        -------
        None
        """
        image_url = data.pop("image", None)
        super().__init__(
            **{
                **data,
                "image_url": image_url
            }
        )


class Tyres(BaseModel):
    """
    Container model representing a paginated collection of Tyre items.

    Attributes:
        tyres (list[Tyre]): List of Tyre instances contained in the current page. Defaults to an empty list.
        current_page (Optional[int]): The current page number (typically 1-based). Set to None when unknown.
        total_pages (Optional[int]): Total number of pages available. Set to None when unknown.
        total_results (Optional[int]): Total number of matching results across all pages. Set to None when unknown.
        has_next_page (Optional[bool]): True if there is a subsequent page available; False if not; None if unknown.
        has_previous_page (Optional[bool]): True if there is a preceding page available; False if not; None if unknown.

    Usage:
        This docstring describes a Pydantic BaseModel used for serializing/deserializing paginated API responses
        that return tyre records. Fields with a None value indicate that pagination metadata was not provided.
    """
    tyres: list[Tyre] = []
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    total_results: Optional[int] = None
    has_next_page: Optional[bool] = None
    has_previous_page: Optional[bool] = None

    def __init__(
        self,
        tyres: list[Tyre] = [],
        current_page: Optional[int] = None,
        total_pages: Optional[int] = None
    ):
        """
        Initialize the pagination schema for a collection of Tyre objects.

        Parameters
        ----------
        tyres : list[Tyre], optional
            List of Tyre objects to include on this page. Defaults to an empty list.
        current_page : Optional[int], optional
            Index of the current page (1-based). If None, pagination state may be partial or unknown.
        total_pages : Optional[int], optional
            Total number of pages available. If None, total/next-page calculation may be limited.

        Behavior
        --------
        This initializer computes and forwards additional pagination metadata to the parent class initializer:
        - total_results is computed by calling self.get_total_results(tyres)
        - has_next_page is computed by calling self.get_has_next_page(current_page, total_pages)
        - has_previous_page is computed by calling self.get_has_previous_page(current_page)

        Returns
        -------
        None

        Raises
        ------
        Any exceptions raised by get_total_results, get_has_next_page, or get_has_previous_page will propagate to the caller.

        Notes
        -----
        Using a mutable default argument for `tyres` (an empty list) is unsafe because the same list instance is shared across calls.
        Prefer using None and creating a fresh list inside the method to avoid unintended shared state.
        """
        super().__init__(
            tyres=tyres,
            current_page=current_page,
            total_pages=total_pages,
            total_results=self.get_total_results(tyres),
            has_next_page=self.get_has_next_page(current_page, total_pages),
            has_previous_page=self.get_has_previous_page(current_page)
        )

    def get_total_results(self, tyres) -> int:
        """
        Return the total number of tyre results.

        Parameters
        ----------
        tyres : Sized
            A collection of tyre items. The object must support len().

        Returns
        -------
        int
            The number of items in the provided tyres collection.

        Raises
        ------
        TypeError
            If the provided tyres object does not support len().
        """
        return len(tyres)

    def get_has_next_page(self, current_page, total_pages) -> Optional[bool]:
        """
        Determine whether there is a next page.

        Parameters
        ----------
        current_page : Optional[int]
            The current page number (parameter is present for signature compatibility;
            the implementation uses self.current_page).
        total_pages : Optional[int]
            The total number of pages (parameter is present for signature compatibility;
            the implementation uses self.total_pages).

        Returns
        -------
        Optional[bool]
            - True if a next page exists (current page is less than total pages).
            - False if no next page exists (current page is greater than or equal to total pages).
            - None if either the current page or total pages value is missing (None).
        """
        if current_page is not None and total_pages is not None:
            return current_page < total_pages
        return None

    def get_has_previous_page(self, current_page) -> Optional[bool]:
        """
        Return whether a previous page exists.

        The method inspects the instance attribute self.current_page. If that attribute
        is set (not None), it returns True when the current page number is greater than 1,
        False when it equals 1 (no previous page). If self.current_page is None, the
        method returns None to indicate the current page is unknown.

        Parameters
        ----------
        current_page
            Present for API compatibility but not used: the method reads self.current_page.

        Returns
        -------
        Optional[bool]
            True if a previous page exists (current page > 1),
            False if on the first page (current page == 1),
            None if the current page is unknown.
        """
        if current_page is not None:
            return current_page > 1
        return None


class TyreSizePredictionResponse(BaseModel):
    """
    Response model for tyre size prediction.

    Attributes:
        status (str): The status of the prediction (e.g., 'success').
        options (list[str]): A list of predicted tyre sizes.
    """
    status: str
    options: list[str]
