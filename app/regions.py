from collections import Counter
import copy
import math
import operator
import os
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath)

# Mapbox token for the choropleth maps
MAPBOX_ACCESS_TOKEN = "pk.eyJ1IjoiYWRlbWlxdWVsIiwiYSI6ImNrcmFiMWxpdTRoZm0ydm1mb3FieHBueHIifQ.8Vz0HX4TMOQN1ywDSEPtSw"
MAPBOX_STYLE = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"


class Electoral_Region():
    """
    Class representing an electoral region. (See https://en.wikipedia.org/wiki/Electoral_district)

    ...
    Attributes
    ----------
    election: elections.Election
        The election this Electoral_Region was part of.
    name: str
        The name of the region.
    level: int
        The level of the region.
    census: int
        The total number of votes registered in the region.
    n_seats: int
        The total number of parliament seats elected in the region.
    votes: dict
        Keys are party names, values are the number of votes that they
        obtained in the region.
    nota: int
        Number of 'None of the Above' votes.
    spoilt_votes: int
        Number of spoilt votes

    Methods
    -------
    compute_election_result(system, valid_parties=None)
        Given an electoral_systems.System, return a collections.Counter with
        the number of seats assigned to each party for the electoral region.

    compute_result(system)
        Given an electoral_systems.System, return an Electoral_Result object
        encoding the results of using that system in the region.

    get_subregions(level):
        Given a region level, regurn a list containing all the subregions at the
        given level.
    """

    def __init__(self, election, name: str, level: int, census: int, n_seats: int, votes: dict, nota: int, spoilt_votes: int):
        """
        Parameters
        ----------
        election: elections.Election
            The election this Electoral_Region was part of.
        name: str
            The name of the region.
        level: int
            The level of the region.
        census: int
            The total number of votes registered in the region.
        n_seats: int
            The total number of parliament seats elected in the region.
        votes: dict
            Keys are party names, values are the number of votes that they
            obtained in the region.
        nota: int
            Number of 'None of the Above' votes.
        spoilt_votes: int
            Number of spoilt votes
        """
        self.election = election
        self.name = name
        self.level = level
        self.census = census
        self.n_seats = n_seats
        self.votes = votes
        self.nota = nota  # None Of The Above (https://en.wikipedia.org/wiki/None_of_the_above)
        self.spoilt_votes = spoilt_votes
        self.total_votes = sum(votes.values())
        return

    def compute_election_result(self, system, valid_parties=None):
        """
        Given an electoral_systems.System, return a collections.Counter with
        the number of seats assigned to each party for the electoral region.

        If a list of valid_parties is given (as strings), only those given
        parties will be considered.
        """
        if valid_parties:
            valid_votes = {p: v for p, v in self.votes.items() if p in valid_parties}
        else:
            vote_threshold = self.total_votes*system.threshold/100
            valid_votes = {k: v for k, v in self.votes.items() if v > vote_threshold}
        round_votes = copy.deepcopy(valid_votes)
        seat_counter = Counter()
        n_seats = copy.deepcopy(self.n_seats)

        if 'LRM' in system.name:  # Largest Remainder Method
            if 'Hare' in system.name:
                seat_cost = sum(valid_votes.values()) / n_seats
            elif 'Droop' in system.name:
                seat_cost = 1 + sum(valid_votes.values()) / (1 + n_seats)
            elif 'HB' in system.name:
                seat_cost = sum(valid_votes.values()) / (1 + n_seats)
            elif 'Imperiali' in system.name:
                seat_cost = sum(valid_votes.values()) / (2 + n_seats)
            remainders = {}
            seats_given = 0
            for party in valid_votes:
                rem, n = math.modf(valid_votes[party] / seat_cost)
                n = int(n)
                seat_counter[party] = n
                remainders[party] = rem
                seats_given += n

            remainders = {k: v for k, v in sorted(remainders.items(), key=lambda item: item[1], reverse=True)}
            for party in remainders:
                if seats_given >= n_seats:
                    break
                seat_counter[party] += 1
                seats_given += 1

            if 'Imperiali' in system.name or 'HB' in system.name:
                if seats_given > self.n_seats:
                    new_system = copy.deepcopy(system)
                    new_system.name = 'LRM-Droop'
                    return self.compute_election_result(new_system)

        else:
            while n_seats != 0:
                best_party = max(round_votes.items(), key=operator.itemgetter(1))[0]
                seat_counter[best_party] += 1
                if system.name == 'dHondt':
                    round_votes[best_party] = valid_votes[best_party] / (seat_counter[best_party] + 1)
                elif system.name == 'SL':  # Sainte-Laguë
                    round_votes[best_party] = valid_votes[best_party] / (2*seat_counter[best_party] + 1)
                n_seats -= 1

        seat_counter = {k: v for k, v in seat_counter.items() if v != 0}
        return seat_counter

    def compute_result(self, system):
        """
        Given an electoral_systems.System, return an Electoral_Result object
        encoding the results of using that system in the region.
        """
        if system.threshold_country:
            valid_parties = self.election.get_valid_parties(system.threshold)
        else:
            valid_parties = None

        result = dict()

        # Note that system.level>=self.level. Otherwise, it doesn't make sense.
        def get_result(region, level):
            if level == system.level:
                result[region.name] = region.compute_election_result(system, valid_parties)
            else:
                for r in region.subregions:
                    get_result(r, level+1)

        get_result(self, self.level)

        return Election_Result(self, system.level, result)

    def get_subregions(self, level):
        """
        Given a region level, regurn a list containing all the subregions at the
        given level.
        """
        subregions = []

        def add_subregions(region):
            if region.level == level:
                subregions.append(region)
            else:
                for r in region.subregions:
                    add_subregions(r)

        add_subregions(self, level)
        return subregions


class Election_Result():
    """
    Encodes the result of a region given a particular level.

    Attributes
    ----------
    region: Electoral_Region
        The region where the result was computed.
    level: int
        The level of the electoral_system.System used for computing the result.
    result: dict
        Keys are region names, values are collection.Counter objects whose keys
        are party names and values are the number of seats obtained.

    Methods
    -------
    get_seat_diff(self, other, region=None, level=None): dict
        Get a dictionary whose keys are party names and results are the
        difference in nuber of seats between the result and 'other'.
    get_lost_votes(self, region=None, level=None): dict
        Get a dictionary whose keys are party names without reprsentation in the
        result and values are the number votes of these parties.
    plot_tooltip(self, other=None): plotly.graph_objects.Figure
        Get the tooltip to show when hovering on the map.
    get_map_plot(self, other=None): plotly.graph_objects.Figure
        Get the choropleth map to be shown on the dashboard.
    get_piechart_plot(self, other=None): plotly.graph_objects.Figure
        Get the pie chart to be shown on the dashboard.
    get_bar_plot(self, metric, other=None): plotly.graph_objects.Figure
        Get the bar chart to be shown on the dashboard.
    """
    def __init__(self, region, level, result):
        """
        Parameters
        ----------
        region: Electoral_Region
            The region where the result was computed.
        level: int
            The level of the electoral_system.System used for computing the result.
        result: dict
            Keys are region names, values are collection.Counter objects whose
            keys are party names and values are the number of seats obtained.
        """
        self.region = region
        self.level = level
        self.result = result

    def get_seat_diff(self, other, region=None, level=None):
        """
        Get a dictionary whose keys are party names and results are the
        difference in nuber of seats between the result and 'other' (which is
        also an object of the class Election_result with the same value for the
        attribute 'region').
        If region or level are specified, they will be the region/level used to
        compute the resulting seat difference. Otherwise, self.region and
        min(self.leve, other.level) will be used.
        """
        if not region:  # Check that self.region==other.region?
            region = self.region
        if not level:
            level = min(self.level, other.level)

        def add_seats(seat_counter, subregion, result):
            if subregion.level == result.level:
                seat_counter += result.result[subregion.name]
            else:
                for r in subregion.subregions:
                    add_seats(seat_counter, r, result)

        seats_1, seats_2 = Counter(), Counter()
        add_seats(seats_1, region, self)
        add_seats(seats_2, region, other)

        seat_diff = {p: seats_1[p]-seats_2[p] for p in set(seats_1).union(set(seats_2))}

        return seat_diff

    def get_lost_votes(self, region=None, level=None):
        """
        Get a dictionary whose keys are party names without reprsentation in the
        result and values are the number votes of these parties.
        If region or level are not specified, self.region/self.level are used.
        """
        if not region:
            region = self.region
        if not level:
            level = self.level

        lost_votes = Counter()

        def compute_subregion_lost_votes(subregion):
            if subregion.level == level:
                for party, votes in subregion.votes.items():
                    if party not in self.result[subregion.name]:
                        lost_votes[party] += votes
            else:
                for r in subregion.subregions:
                    compute_subregion_lost_votes(r)

        compute_subregion_lost_votes(region)

        return lost_votes

    def _get_piechart_trace(self, region=None):
        result = Counter()

        if not region:
            for vote_counter in self.result.values():
                result += vote_counter
        else:
            def add_vote_counter(subregion, result):
                if subregion.level == self.level:
                    result += self.result[subregion.name]
                else:
                    for r in subregion.subregions:
                        add_vote_counter(r, result)

            add_vote_counter(region, result)

        labels = list(result.keys())
        colors = [self.region.election.colors[x] if x in self.region.election.colors else '#7D7D7D' for x in labels]

        pie = go.Pie(
            labels=labels,
            values=[result[x] if x in result else 0 for x in labels],
            marker_colors=colors,
            hole=.4,
            hoverinfo="label+percent+name",
            textinfo='value',
            textfont_size=10,
            textposition='inside',
        )
        return pie

    def _get_lost_votes_trace(self, lost_votes, n):
        party_lost_votes = lost_votes.most_common(n)
        bar_colors = [self.region.election.colors[x[0]] if x[0] in self.region.election.colors else '#7D7D7D' for x in party_lost_votes]
        bar = go.Bar(
            x=[x[0] for x in party_lost_votes],
            y=[x[1] for x in party_lost_votes],
            marker_color=bar_colors,
        )
        return bar

    def plot_tooltip(self, other=None):
        """
        Get the tooltip to show when hovering on the map.
        If 'other' result is specified, the tooltip plots the pie charts of the
        seat distribution of self and other. Note that the self.region and
        other.region must be the same one.
        Otherwise, plot the seat distribution of the region together with a bar
        chart of lost votes.
        """
        plot_title = self.region.name

        if not other:
            lost_votes = self.get_lost_votes()
            n_lost_votes = sum(lost_votes.values())
            tooltip = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'xy'}]])
            tooltip.add_trace(self._get_piechart_trace(), 1, 1)
            tooltip.add_trace(self._get_lost_votes_trace(lost_votes, n=4), 1, 2)
            tooltip.update_xaxes(showticklabels=False)
            plot_title += '\t ({:,} -- {:.2f}%)'.format(n_lost_votes, 100*n_lost_votes/self.region.total_votes)
        else:  # If other is actually another result ---> Compare piecharts
            # TODO Check that self.region == other.region
            tooltip = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
            tooltip.add_trace(self._get_piechart_trace(), 1, 1)
            tooltip.add_trace(other._get_piechart_trace(), 1, 2)

        tooltip.update_layout(
            title_text=plot_title,
            margin=dict(t=40, b=10, l=0, r=0),
            uniformtext_minsize=8,
            uniformtext_mode='hide',
            width=300,
            height=150,
            showlegend=False,
        )

        return tooltip

    def get_map_plot(self, other=None):
        """
        Get a figure with the choropleth map.
        If 'other' result is specified, compute the seat difference between self
        and other for every region.
        Otherwise, compute the percentage of lost votes of every region.
        """
        if not other:  # Means that we're computing Lost Votes
            locations = list(self.result.keys())
            lost_votes_percentage = []
            for region_name in locations:
                region = self.region.election.get_region(self.level, region_name)
                region_lost_votes = self.get_lost_votes(region)
                n_region_lost_votes = sum(region_lost_votes.values())
                n_region_votes = sum(region.votes.values())
                lost_votes_percentage.append(n_region_lost_votes / n_region_votes)

            map = go.Figure(go.Choroplethmapbox(
                geojson=self.region.election.country.get_geojson(self.level),
                locations=locations,
                z=lost_votes_percentage,
                colorscale="Reds",
                zmin=0, zmax=1,
                marker_line_width=1,
                hoverinfo='none',
            ))
            map.update_layout(title='Percentage of Lost Votes per Region')

        else:  # Means that we're computing Seat Difference
            if self.level <= other.level:
                locations = list(self.result.keys())
                level = self.level
            else:
                locations = list(other.result.keys())
                level = other.level

            seat_diff = []
            for region_name in locations:
                region = self.region.election.get_region(level, region_name)
                seat_diff_counter = self.get_seat_diff(other, region=region, level=level)
                n_different_seats = sum([x for x in seat_diff_counter.values() if x > 0])
                seat_diff.append(n_different_seats)

            map = go.Figure(go.Choroplethmapbox(
                geojson=self.region.election.country.get_geojson(level),
                locations=locations,
                z=seat_diff,
                colorscale="Reds",
                zmin=0, zmax=max(10, max(seat_diff)),
                marker_line_width=1,
                hoverinfo='none',
                ),
            )
            map.update_layout(title='Seat difference per Region')

        map.update_layout(
            mapbox_style="light",
            mapbox_accesstoken=MAPBOX_ACCESS_TOKEN,
            mapbox_zoom=region.election.country.zoom,
            mapbox_center=region.election.country.center,
            margin={"r": 0, "t": 40, "l": 0, "b": 0},
            height=900,
            font={'size': 16},
        )

        return map

    def get_piechart_plot(self, other=None):
        """
        Get a figure plotting a pie chart with the seat distribution of the
        result. If 'other' is specified, two pie charts will be shown in the
        plot, one per result.
        """
        if not other:
            fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'domain'}]])
            fig.add_trace(self._get_piechart_trace(), 1, 1)
        else:
            fig = make_subplots(rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]])
            fig.add_trace(self._get_piechart_trace(), 1, 1)
            fig.add_trace(other._get_piechart_trace(), 1, 2)
            fig.update_layout(
                annotations=[dict(text='Sys. 1', x=0.18, y=0.5, font_size=20, showarrow=False),
                             dict(text='Sys. 2', x=0.82, y=0.5, font_size=20, showarrow=False)],
            )

        fig.update_traces(hole=.4, hoverinfo="label+percent+name", textinfo='value', textfont_size=20, textposition='inside')
        fig.update_layout(
            title="Final results",
            font={'size': 16},
            margin=dict(t=40, b=10, l=0, r=0),
            uniformtext_minsize=12,
            uniformtext_mode='hide',
        )

        return fig

    def get_bar_plot(self, metric, other=None):
        """
        Get the bar plot figure.
        If the metric specified is 'Lost Votes', 10 parties with most lost votes
        will be shown.
        If the metric specified is 'Seat Difference', 'other' needs to be
        specified, and all the parties with a nonzero seat difference will be
        shown.
        """
        if metric == 'Lost Votes':
            lost_votes = self.get_lost_votes()
            bar = self._get_lost_votes_trace(lost_votes, n=10)
            fig = go.Figure(data=[bar])
            total_lost_votes = sum(lost_votes.values())
            total_votes = sum(self.region.votes.values())
            bar_title = 'Lost Votes per Party\t (Total Lost Votes: {:,} -- {:.2f}%)'.format(total_lost_votes, 100 * total_lost_votes / total_votes)
            yaxis_bar_title = 'Lost Votes'
        elif metric == 'Seat Difference':
            if not other:
                raise TypeError("The second Election_Result object shouldn't be None")
            seat_diff = self.get_seat_diff(other)
            seat_diff = {k: v for k, v in seat_diff.items() if v != 0}
            seat_diff = dict(sorted(seat_diff.items(), key=lambda item: item[1], reverse=True))
            bar_colors = [self.region.election.colors[k] if k in self.region.election.colors else '#7D7D7D' for k in seat_diff.keys()]
            fig = go.Figure(data=[go.Bar(
                x=[k for k in seat_diff.keys()],
                y=[v for v in seat_diff.values()],
                marker_color=bar_colors,
            )])
            n_different_seats = sum([x for x in seat_diff.values() if x > 0])
            bar_title = 'Total Seat Difference\t ({}/{} -- {:.2f}%)'.format(n_different_seats,
                                                                            self.region.n_seats,
                                                                            100 * n_different_seats / self.region.n_seats)
            yaxis_bar_title = 'Seats Sys 1 - Seats Sys 2'

        fig.update_layout(
            title=bar_title,
            yaxis=dict(
                title=yaxis_bar_title,
                titlefont_size=16,
                tickfont_size=14,
            ),
            font={'size': 16},
            margin=dict(t=40, b=20, l=0, r=0),
        )

        return fig
