import random
import sys

def bubble(inputArray):
	x = 1

	error = 100
	errorImprovement = 9
	errorFunctionTest = False

	accuracy = 0
	accuracyImprovement = 9
	accuracyFunctionTest = True

	for i in range(0, len(inputArray)):
		for j in range(0, len(inputArray)-1):
			if (i*len(inputArray))%((len(inputArray)**2)*0.1) == 0 and i != 0 and j == 0:
				print("Algorithm still working fine")
				x += 1

				if errorFunctionTest:
					error = error - errorImprovement
					errorImprovement = errorImprovement - 1
					if errorImprovement < 0:
						errorImprovement = 0
					print("Loss function " + str(error))

				if accuracyFunctionTest:
					accuracy = accuracy + accuracyImprovement
					accuracyImprovement = accuracyImprovement - 1
					if accuracyImprovement < 0:
						accuracyImprovement = 0
					print("Accuracy function " + str(accuracy))

			if inputArray[j] > inputArray[j+1]:
				tmp = inputArray[j+1]
				inputArray[j+1] = inputArray[j]
				inputArray[j] = tmp

	return [inputArray]

if __name__ == "__main__":

	inputArray = random.sample(range(10000), 2000)
	bubble(inputArray)
	print("Finished Bubblesort")
