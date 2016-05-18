class ILoop(object):
    objects = []

    def add_object(self, obj):
        """
        Add object to the pool of objects
        :param obj: Updatable object
        :type obj: interfaces.IUpdatable
        """
        raise NotImplementedError

    def tick(self):
        """
        Process update method of all objects
        """
        raise NotImplementedError

    def start(self):
        """
        Init loop and start reactor
        """
        raise NotImplementedError


class IUpdatable(object):
    def update(self, t):
        """
        :param t: Time, passed since last update
        :type t: float
        """
        raise NotImplementedError


class ICar(object):
    def get_speed(self):
        """
        Get value of car's heading
        :return: Value of car's heading
        :rtype: float
        """
        raise NotImplementedError

    def get_heading(self):
        """
        Get value of car's speed
        :return: Value of car's speed
        :rtype: float
        """
        raise NotImplementedError

    def get_location(self):
        """
        Get current car's location
        :return: Value of car's speed
        :rtype: utils.GeoPoint
        """
        raise NotImplementedError

    def get_odometer_value(self):
        """
        Get path length since start of car
        :return: Value of car's mileage
        :rtype: float
        """
        raise NotImplementedError
