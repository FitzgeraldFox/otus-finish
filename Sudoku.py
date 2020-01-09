from itertools import product

class Sudoku:
    def solve(self, size, grid):
        boxRowsCount, boxColumnsCount = size
        dimension = boxRowsCount * boxColumnsCount
        cellValuesByConstraint = (
             [("cellConstraint", rc) for rc in product(range(dimension), range(dimension))] +
             [("rowConstraint", rn) for rn in product(range(dimension), range(1, dimension + 1))] +
             [("columnConstraint", cn) for cn in product(range(dimension), range(1, dimension + 1))] +
             [("boxConstraint", bn) for bn in product(range(dimension), range(1, dimension + 1))])
        constraintsRelatedToCellValue = dict()
        for rowIndex, colIndex, number in product(range(dimension), range(dimension), range(1, dimension + 1)):
            boxNumber = (rowIndex // boxRowsCount) * boxRowsCount + (colIndex // boxColumnsCount) # Box number
            constraintsRelatedToCellValue[(rowIndex, colIndex, number)] = [
                ("cellConstraint", (rowIndex, colIndex)),
                ("rowConstraint", (rowIndex, number)),
                ("columnConstraint", (colIndex, number)),
                ("boxConstraint", (boxNumber, number))
            ]
        cellValuesByConstraint, constraintsRelatedToCellValue = self.__exact_cover(cellValuesByConstraint, constraintsRelatedToCellValue)

        # Проходимся по каждой ненулевой ячейке оригинальной матрицы
        for i, row in enumerate(grid):
            for j, number in enumerate(row):
                if number:
                    # Сокращаем значения матрицы cellValuesByConstraint,
                    # удаляя значения ячеек, которые противоречат текущим значениям матрицы
                    self.__select(cellValuesByConstraint, constraintsRelatedToCellValue, (i, j, number))

        for solution in self.__solve(cellValuesByConstraint, constraintsRelatedToCellValue, []):
            for (rowIndex, colIndex, number) in solution:
                grid[rowIndex][colIndex] = number
        return grid

    # Создаём матрицу покрытия
    def __exact_cover(self, cellValuesByConstraint, constraintsRelatedToCellValue):
        cellValuesByConstraint = {j: set() for j in cellValuesByConstraint}
        for cellValue, row in constraintsRelatedToCellValue.items():
            for constraint in row:
                cellValuesByConstraint[constraint].add(cellValue)
        return cellValuesByConstraint, constraintsRelatedToCellValue

    def __solve(self, cellValuesByConstraint, constraintsRelatedToCellValue, solution):
        if not cellValuesByConstraint:
            yield list(solution)
        else:
            # Выбираем ограничение (ключ) элемента
            # с наименьшим количеством значений
            condition = min(cellValuesByConstraint, key=lambda c: len(cellValuesByConstraint[c]))
            for rowColValue in list(cellValuesByConstraint[condition]):
                solution.append(rowColValue)
                cols = self.__select(cellValuesByConstraint, constraintsRelatedToCellValue, rowColValue)
                for s in self.__solve(cellValuesByConstraint, constraintsRelatedToCellValue, solution):
                    yield s
                self.__deselect(cellValuesByConstraint, constraintsRelatedToCellValue, rowColValue, cols)
                solution.pop()

    # Проходимся по каждой ненулевой ячейке оригинальной матрицы,
    # перебираем каждое ограничение этой ненулевой ячейки,
    # перебираем все значения, которые удовлетворяют
    # этому конкретному ограничению и каким-то другим,
    # вычёркиваем значения ячейки из других ограничений,
    # которые не совпадают с текущим рассматриваемым ограничением
    # как невозможные по причине противоречий условиям ненулевой ячейки,
    # запоминаем вычеркнутые ячейки в массив cols,
    # чтобы потом восстановить их.
    def __select(self, cellValuesByConstraint, constraintsRelatedToCellValue, rowColValue):
        cols = []
        # Перебираем каждое ограничение этой ненулевой ячейки
        for constraint in constraintsRelatedToCellValue[rowColValue]:
            if constraint not in cellValuesByConstraint:
                continue
            # Проходим по всем
            # значениям, которые могли бы быть
            # в этой ячейке в этой строке и столбце
            for cellValue in cellValuesByConstraint[constraint]:
                # По конкретному значению,
                # которое могло бы быть в этой ячейке,
                # проходим по всем условиям,
                # которым удовлетворяет потенциальное значение
                for cellValueConstraint in constraintsRelatedToCellValue[cellValue]:
                    # Если условие потенциального значения
                    # не совпадает с текущим условием
                    # для переданного значения
                    if cellValueConstraint != constraint:
                        # Удаляем из матрицы покрытия cellValuesByConstraint
                        # данный индекс потенциального значения
                        # (rowIndex, columnIndex, numberValue)
                        # как противоречащий переданному значению ячейки.
                        # Например:
                        # rowColValue = (0,0,5)
                        # constraint = ('rowConstraint',(0,0))
                        # i = (0,0,7)
                        # k = ('columnConstraint',(0,7))
                        # k != constraint и i не может удовлетворять условию k
                        # пока есть rowColValue
                        cellValuesByConstraint[cellValueConstraint].remove(cellValue)
            # Сохраняем в массив cols вычеркнутые строки, чтобы их потом восстановить
            cols.append(cellValuesByConstraint.pop(constraint))
        return cols

    # Восстанавливаем значения, которые были сохранены в cols на каждом уровне рекурсии
    def __deselect(self, cellValuesByConstraint, constraintsRelatedToCellValue, rowColValue, cols):
        # Берём ограничения по значению ячейки
        # в обратном порядке
        for constraint in reversed(constraintsRelatedToCellValue[rowColValue]):
            # Берём последнее значение из cols.
            # Оно соответствует ячейкам, вычеркнутым на
            # этом уровне рекурсии
            cellValuesByConstraint[constraint] = cols.pop()
            for cellValue in cellValuesByConstraint[constraint]:
                for cellValueConstraint in constraintsRelatedToCellValue[cellValue]:
                    if cellValueConstraint != constraint:
                        cellValuesByConstraint[cellValueConstraint].add(cellValue)