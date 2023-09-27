from accountpool.scheduler import Scheduler
import argparse

parser = argparse.ArgumentParser(description='AccountPool')
parser.add_argument('website', type=str, help='website')
parser.add_argument('--processor', type=str, help='processor to run')
args = parser.parse_args()
website = args.website
# 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
if __name__ == '__main__':
    if args.processor:
        getattr(Scheduler(), f'run_{args.processor}')(website)
    else:
        Scheduler().run(website)
        print('run')