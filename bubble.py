import random
import sys

def bubble(inputArray):
	x = 1

	loss = 100
	lossImprovement = 25
	lossFunctionTest = True

	accuracy = 0
	accuracyImprovement = 25
	accuracyFunctionTest = True

	progress = 0

	for i in range(0, len(inputArray)):
		for j in range(0, len(inputArray)-1):
			if (i*len(inputArray))%((len(inputArray)**2)*0.1) == 0 and i != 0 and j == 0:
				print("Algorithm still working fine")
				#print("This is an error message")
				progress += 10
				print("Progress Information " + str(progress) + " %")
				x += 1

				if lossFunctionTest:
					loss = loss - lossImprovement
					lossImprovement = lossImprovement - 1
					if lossImprovement < 0:
						lossImprovement = 0
					print("Loss function " + str(loss))

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

	inputArray = random.sample(range(10000), 8000)
	bubble(inputArray)
	print("Finished Bubblesort")
