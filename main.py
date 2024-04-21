from models.main import Model
from views.main import View
from controllers.main import Controller
from PIL import Image


def main():
    model = Model()
    view = View()
    controller = Controller(model, view)
    controller.start()


if __name__ == "__main__":
    main()
