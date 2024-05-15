class Logger:
    def __init__(self, wandb_project, wandb_entity):
        self.wandb_project = wandb_project
        self.wandb_entity = wandb_entity

        if self.wandb_project and self.wandb_entity:
            import wandb

            wandb.init(project=self.wandb_project, entity=self.wandb_entity)

    def log(self, name, value):
        if self.wandb_project and self.wandb_entity:
            wandb.log({name: value})

        else:
            print({name: value})
