from abc import ABC, abstractmethod
from typing import Optional, Type

from game.core.ai import AIBase, AIDefault
from game.core.cheker import CheckerDefault, CheckerBase, verify_checker_instance
from game.core.players.player import PlayerBase, PlayerT
from game.core.players.players import verify_players_instance, PlayersT
from game.core.result import ResultCode, GameState, GameStateT
from game.core.table.annotations import CombType, CellIndex
from game.core.table.table import verify_table_instance, GameFieldType, TableT


class GameBase(ABC):
    def __init__(self,
                 players: PlayersT,
                 table: TableT,
                 game_state: GameStateT):

        self._players = players
        self._table = table
        self._game_state = game_state
        """Game state. By default, it is indicated that the result is missing. changes as the game progresses"""

    @property
    def players(self) -> PlayerT:
        """Returns an instance of the Players class"""
        return self._players

    @property
    def game_field(self) -> GameFieldType:
        """Returns the playing field from a Table instance"""
        return self.table.game_field

    @property
    def current_player(self) -> PlayerT:
        return self._players.current_player

    @property
    def table(self) -> TableT:
        return self._table

    @property
    def game_state(self) -> GameStateT:
        return self._game_state

    def set_get_next_player(self) -> PlayerT:
        """
        Replaces the current player with the next player in line and returns it.
        New current player available via self.current_player
        * this function is the same as self.table.set_get_next_player
        """
        return self._players.set_get_next_player()

    @abstractmethod
    def step(self, index_row: int, index_column: int, player: PlayerBase):
        """
        Places a player symbol on the playing field 'self.table'\n
        * Added symbol in a game field
        * Added +1 step in a player.count_step
        """
        ...

    @abstractmethod
    def result(self, player: PlayerBase) -> GameStateT:
        """
        The function checks the cells for the player given in the argument and returns its game_state\n
        The game_state matches the logical end when:\n
        * game_state.code.WINNER + game_state.win_player and game_state.win_combination
        * game_state.code.ALL_CELLS_USED

        Returns self.game_state.
        """
        ...

    @abstractmethod
    def step_result(self, index_row: int, index_column: int, player: PlayerBase) -> GameStateT:
        """
        Sets the symbol for the given player by the given indices and returns its result \n
        This is a unifying function. It includes:\n
        * def self.step
        * def self.result

        Return: self.result: GameState.
        """

    @abstractmethod
    def ai_get_step(self, player: PlayerBase) -> CellIndex:
        ...

    @abstractmethod
    def ai_step(self, player: PlayerBase):
        ...

    @abstractmethod
    def ai_step_result(self, player: PlayerBase) -> GameStateT:
        ...

    @abstractmethod
    def set_winner(self, player: PlayerBase, win_combination: CombType):
        """
        Changes the self._game_state parameter to the result of the game in which there is a winner. \n
        Changes: \n
        * Replaces the result code \n
        * Add a reference to the winning player object \n
        * Add a player winning combination.
        """

    @abstractmethod
    def set_draw(self):
        """
        Changes the self._game_state parameter to the result of a game in which all cells are used and
        there is no winner – i.e., a draw. \n
        Changes: \n
        * Replaces the result code.
        """


class Game(GameBase):
    def __init__(self,
                 players: PlayersT,
                 table: TableT,
                 game_state: GameStateT = GameState(),
                 checker: Type[CheckerBase] | CheckerBase = CheckerDefault,
                 ai: Type[AIBase] | AIBase = AIDefault):

        verify_players_instance(players)
        verify_table_instance(table)
        verify_checker_instance(checker)
        super().__init__(players=players, table=table, game_state=game_state)

        self._checker = checker
        self._ai = ai

    def step(self, index_row: int, index_column: int, player: PlayerBase):
        self.table.set_symbol_cell(index_row=index_row, index_column=index_column, symbol=player.symbol)
        player.add_count_step()

    def result(self, player: PlayerBase) -> GameStateT:
        if player.count_steps >= self.table.param.COMBINATION:

            if win_comb := self._get_win_comb(player=player):
                self.set_winner(player=player, win_combination=win_comb)

            elif self._get_draw_result():
                self.set_draw()
        return self.game_state

    def step_result(self, index_row: int, index_column: int, player: PlayerBase) -> GameStateT:
        self.step(index_row=index_row, index_column=index_column, player=player)
        return self.result(player=player)

    def ai_get_step(self, player: PlayerBase) -> CellIndex:
        return self._ai.get_step(symbol=player.symbol, table=self.game_field, combinations=self.table.combinations)

    def ai_step(self, player: PlayerBase):
        i_row, i_column = self.ai_get_step(player=player)
        self.step(index_row=i_row, index_column=i_column, player=player)

    def ai_step_result(self, player: PlayerBase) -> GameStateT:
        i_row, i_column = self.ai_get_step(player=player)
        return self.step_result(index_row=i_row, index_column=i_column, player=player)

    def set_winner(self, player: PlayerBase, win_combination: CombType):
        self.game_state.update(code=ResultCode.WINNER, win_player=player, win_combination=win_combination)

    def set_draw(self):
        self.game_state.update(code=ResultCode.ALL_CELLS_USED)

    def _get_win_comb(self, player: PlayerBase) -> Optional[CombType]:
        return self._checker.result_player(player.symbol,
                                           table=self.table.game_field,
                                           combinations=self.table.combinations)

    def _get_draw_result(self) -> bool:
        if self.table.count_free_cells == 0:
            return True
