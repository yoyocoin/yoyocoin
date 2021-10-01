class SumTree:
    def __init__(self, left=None, right=None, value=None, data=None):
        """ SumTree node
        :param left: left node object
        :param right: right node object
        :param value: node value
        :param data: node data
        """
        self._left = left
        self._right = right

        self._value = value
        self._data = data
        if left:
            self.sum = self._left.sum + self._right.sum
        else:
            self.sum = self._value

    def search(self, value: int, offset: int = 0):
        if self._value:
            return self._data
        if self._left.sum + offset > value:
            return self._left.search(value, offset=offset)
        return self._right.search(value, offset=offset + self._left.sum)

    @classmethod
    def _build_tree(cls, arr: list):
        n_arr = []
        for i in range(0, len(arr), 2):
            if i + 1 < len(arr):
                n_arr.append(cls(left=arr[i], right=arr[i + 1]))
            else:
                n_arr.append(cls(left=arr[i], right=cls(value=0)))
        if len(n_arr) > 1:
            return cls._build_tree(n_arr)
        else:
            return n_arr[0]

    @classmethod
    def from_dict(cls, k_v_data: dict):
        """ Create SumTree from dict
        value: value that is sumed
        data:  data returned on search
        """
        arr = [cls(value=v, data=d) for d, v in k_v_data.items()]
        return cls._build_tree(arr)
